import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, \
                            QLineEdit, QHBoxLayout, QLabel, QMessageBox, \
                            QFileDialog
from PyQt5.QtGui import QFont
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

from boundarycollision import BoundaryCollisionDetector
from trackabledot import TrackableDot
import random
import time

FACE_COLOR = 'white'
RADIUS = 0.3
DT = 0.05
COLOR = 'black'
SELECTION_COLOR = 'gray'
BLINKING_COLOR = 'yellow'
INCORRECT_COLOR = 'red'
UNSELECTED_COLOR = 'green'
START_FULLSCREEN = True
NUMBER_OF_DOTS = 10
NUMBER_OF_TRACK_DOTS = 2
VELOCITY = 3 # in data units / s
BLINKING_DURATION = 2 * 1000 # in ms
TRIAL_DURATION = 3 * 1000 # in ms
INTERVAL = 30 # in ms
TRIAL_DICTIONARY = {0: 2, 1: 2, 2: 2, 3: 3, 4: 3,
                    5: 3, 6: 3, 7: 3, 8: 4, 9: 4,
                    10: 4, 11: 4, 12: 5, 13: 5, 14: 5, 15: 5} # Follows {trial: NUM_DOTS}


class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        # a figure instance to plot on
        self.figure = Figure(facecolor=FACE_COLOR)

        # This is to make the QDialog Window full size.
        if START_FULLSCREEN:
            self.showMaximized()
            self.setFixedSize(self.size())


        self.canvas = FigureCanvas(self.figure)

        # Steup the figures axis, margins, and background color.
        self.setup_figure()

        # setup the gui
        self.setup_ui()

        # initialize the dots list
        self.dots = []
        self.tracked_dots = {}
        self.highlighted_dot = None

        # keep track of the trials
        self.dot_motion_active = False
        self.clicking_active = False
        self.trial_dictionary = TRIAL_DICTIONARY
        self.trial_id = 0
        self.trial_clicks = self.trial_dictionary[self.trial_id]
        self.clicked_dots = []
        self.trial_starts = []
        self.trial_durations = []
        self.correct_dots = np.sort(list(self.trial_dictionary.values()))
        self.total_duration = 0
        self.output_file = ""
        self.mouse_pressed = False

    def setup_dots(self):
        """Removes any dots on the canvas and generates a new list of them.
        This method does not draw them or add them to the canvas.
        """
        self.remove_dots()
        for i in range(NUMBER_OF_DOTS):
            self.dots.append(TrackableDot((self.generate_location(self.dots, RADIUS)), RADIUS, COLOR, self.generate_velocity(VELOCITY), i))

    def draw_dots(self):
        """Uses the dots list and adds the circles to the canvas and draws them.
        This method does not create the circle objects.
        """
        for i in range(len(self.dots)):
            self.ax.add_artist(self.dots[i])
        self.canvas.draw()

    def track_dots(self):
        """Sets up a dictionary and in order to start the tracking.
        Args:
            num: an integer less than NUMBER_OF_DOTS, this determines the number
            of tracked dots.
        """
        self.tracked_dots = {}
        for i in range(self.trial_clicks):
            self.tracked_dots[self.dots[i].id] = (self.dots[i])

    @property
    def valid_click(self):
        return self.trial_clicks > 0 and self.clicking_active

    def generate_velocity(self, mag=1.0):
        """Generate a velocity with magnitude of mag.
        Returns:
            vel: a velocity vector as a 2-tuple
        """
        vel = np.random.uniform(-1,1), np.random.uniform(-1,1)
        normalization = np.sqrt(vel[0]**2 + vel[1]**2)
        return vel[0]/normalization * mag, vel[1]/normalization * mag

    def generate_location(self, dots_list, radius):
        """Generates a location using the width and height of the window.
        Args:
            dots_list: a list of generated dots, used to prevent location collisions
            radius: the size of the dots in the list
        Returns:
            a tuple which represents the location.
        """
        location = (np.random.uniform(0.1, 0.9) * self.WIDTH, np.random.uniform(0.1, 0.9) * self.HEIGHT)
        should_restart = True
        while should_restart:
            should_restart = False
            for dot in dots_list:
                if (np.sqrt((location[0] - dot.center[0])**2 + (location[1] - dot.center[1])**2)) < (5 * radius):
                    location = (np.random.uniform(0.1, 0.9) * self.WIDTH, np.random.uniform(0.1, 0.9) * self.HEIGHT)
                    should_restart = True
                    break
        return location

    def grab_default_dimensions(self):
        """Stores default dimensions in order to allow resizing after tracking
        has ended.
        """
        self.DEFAULT_MINSIZE = self.minimumSize()
        self.DEFAULT_MAXSIZE = self.maximumSize()
        self.WIDTH = self.figure.get_figwidth()
        self.HEIGHT = self.figure.get_figheight()

    def reset_sizing(self):
        self.setMinimumSize(self.DEFAULT_MINSIZE)
        self.setMaximumSize(self.DEFAULT_MAXSIZE)

    def setup_ui(self):
        """Sets up two BoxLayouts(a vertical and a horizontal) with two buttons
        and a text box. It also holds our matplotlib window.
        """
        # track button setup
        self.track_button = QPushButton('Begin Tracking')
        self.track_button.clicked.connect(self.begin_tracking_button_clicked)
        self.track_button.setMaximumWidth(200)

        # stop button setup
        # self.stop_button = QPushButton('Stop Tracking')
        # self.stop_button.clicked.connect(self.stop_tracking_button_clicked)
        # self.stop_button.setEnabled(False)
        # self.stop_button.setMaximumWidth(200)

        # text field setup
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Participant ID")
        self.text_field.setMaximumWidth(200)

        # next button setup
        self.next_button = QPushButton('Next Trial')
        self.next_button.clicked.connect(self.next_button_clicked)
        self.next_button.setEnabled(False)
        self.next_button.setMaximumWidth(200)

        # Info label setup
        self.info_label = QLabel("Trial #0 -- 2 Clicks Left")
        self.info_label.setMaximumWidth(300)
        self.info_label.setMinimumWidth(300)
        self.info_label.setMaximumHeight(20)
        self.info_label.setFont(QFont("Arial",12, QFont.Normal ))

        # Set up the bottom layout
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.track_button)
        #self.bottom_layout.addWidget(self.stop_button)
        self.bottom_layout.addWidget(self.info_label)
        self.bottom_layout.addWidget(self.next_button)
        self.bottom_layout.addWidget(self.text_field)

        # set up the message box
        self.pid_message = QMessageBox()
        self.pid_message.setIcon(QMessageBox.Critical)
        self.pid_message.setText("Please add a Participant ID.")
        self.pid_message.setStandardButtons(QMessageBox.Ok)

        # set up stop message box
        self.stop_message = QMessageBox()
        self.stop_message.setIcon(QMessageBox.Critical)
        self.stop_message.setText("Are you sure you would like to stop tracking?")
        self.stop_message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        self.save_message = QMessageBox()
        self.save_message.setIcon(QMessageBox.Information)
        self.save_message.setText("")
        # set the whole layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(self.bottom_layout)
        self.setLayout(layout)

    def remove_dots(self):
        """Iterate through the dots array and delete them while removing them
        from the canvas.
        """
        for dot in self.dots:
            dot.remove()
        self.dots = []
        self.canvas.draw()

    def closeEvent(self, event):
        """This method is called when the application is closing.
        Disconnects the event handler which tracks the clicking.
        """
        print("The window will close.")
        try:
            self.figure.canvas.mpl_disconnect(self.cid)
        except AttributeError:
            pass
        try:
            self.line_ani._stop()
        except AttributeError:
            pass
        event.accept()

    def resizeEvent(self,event):
        """Handles resize event and updates the default dimesions.
        """
        self.grab_default_dimensions()

    def display_pid_message(self):
        """Displays a message which requires a PID to be entered.
        """
        self.pid_message.exec_()

    def next_button_clicked(self):
        """Start the trial and updates the instance variables about the current
        trial. Make sure that clicking is not active and a new trial is ok to
        begin.
        """
        if not self.clicking_active:
            if self.trial_id == 1:
                self.total_duration = time.time()
            self.update_info_label()
            self.setup_dots()
            self.draw_dots()
            self.canvas.draw()
            self.track_dots()
            self.animate_plot()
            self.canvas.draw()

    def begin_tracking_button_clicked(self):
        """Action when tracking button clicked.
        Validate the textField.text value and begin the animation sequence.
        """
        self.grab_default_dimensions()
        self.ax.set_ylim([0, self.HEIGHT])
        self.ax.set_xlim([0, self.WIDTH])
        if (self.has_valid_pid()):
            self.next_button.setEnabled(True)
            self.text_field.setReadOnly(True)
            self.track_button.setEnabled(False)
            self.track_button.setText('Tracking ...')
        else:
            self.display_pid_message()

    def stop_tracking_button_clicked(self, event):
        """Checks to see if tracking is currently active, if it is it stops
        the animation and allows the window to be resized.
        """
        retval = self.stop_message.exec_()
        if retval == QMessageBox.Yes:
            self.text_field.setReadOnly(False)
            self.canvas.draw()
            self.track_button.setEnabled(True)
            self.track_button.setText('Begin Tracking')
            self.remove_dots()
            try:
                self.dot_ani._stop()
            except AttributeError:
                pass


    def has_valid_pid(self):
        """Makes sure that the PID field is not empty.
        Returns:
            bool: True if it has a valid pid.
        """
        if self.text_field.text() != "":
            return True
        return False


    def update_dots(self, i):
        """Uses the velocity values of the dot and the detector class in order
        to update the position of the dots.
        Args:
            i: generator for the animation
        """
        detector = BoundaryCollisionDetector(self)
        for dot in self.dots:
            dot.update_position(DT)
            dot.colliding = detector.detect_collision(dot)
        for dot in self.dots:
            detector.update_velocity(dot)
        return self.dots

    def _blink_stage(self, i):
        """Uses stored values to use one animation function to first blink
        then move the dots.
        Args:
            i: the current iteration value
        Returns:
            blinking: a boolean which denotes if it is in the blinking stage.
        """
        num_iter = int(TRIAL_DURATION/INTERVAL)
        if (i < int(num_iter / TRIAL_DURATION * BLINKING_DURATION)):
            return True
        else:
            return False

    def conduct_subtrial(self, i):
        """Runs the animation of a sub trial. Modifies a instance variable which
        keeps track whether the trial is active.
        Args:
            sub_id: uses the TRIAL_DICTIONARY to determine the setup.
            i: generator for the animation
        """
        if (self._blink_stage(i)):
            if i == 0:
                #self.stop_button.setEnabled(False)
                self.next_button.setEnabled(False)
                self.dot_motion_active = True
            if i % 6 == 0:
                self.blink_dots(i)
        elif (i + 1 == int(TRIAL_DURATION/INTERVAL)):
            self.dot_motion_active = False
            self.clicking_active = True
            self.next_button.setEnabled(False)
            self.trial_starts.append(time.time())
        else:
            self.update_dots(i)

    def animate_plot(self):
        """Wrapper that runs the animation.
        """
        self.dot_ani = animation.FuncAnimation(self.figure, self.conduct_subtrial, int(TRIAL_DURATION/INTERVAL), interval=INTERVAL, repeat=False)

    def blink_dots(self, i):
        """Uses the dictionary of tracked dots and blinks them.
        """
        for dot in self.tracked_dots.values():
            if dot.color == BLINKING_COLOR:
                dot.set_color(COLOR)
                dot.color = COLOR
            else:
                dot.set_color(BLINKING_COLOR)
                dot.color = BLINKING_COLOR


    def setup_figure(self):
        '''Setup figure to eliminate the toolbar and resizing.
        Presents the figure.
        '''
        # Remove toolbar
        mpl.rcParams['toolbar'] = 'None'

        # instead of ax.hold(False)
        self.figure.clear()

        self.ax = self.figure.add_subplot(111)


        # Remove ticks and labels on axis
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim([0,1])
        self.ax.set_ylim([0,1])
        self.ax.axis('off')

        # Remove margin on plot.
        self.figure.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.00)

        # refresh canvas
        self.canvas.draw()
        self.cid = self.figure.canvas.mpl_connect('button_release_event', self.onrelease)
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.cid = self.figure.canvas.mpl_connect('motion_notify_event', self.onmouse)

    def _distance(self, loc1, loc2):
        """Outputs distance between two tuples (x, y)
        Args:
            loc1/2: locations for distances to be computed
        Returns:
            dist: float value of distance
        """
        return np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

    def update_info_label(self):
        new_string = "Trial #{} -- {} Clicks Left".format(self.trial_id, self.trial_clicks)
        self.info_label.setText(new_string)
        self.info_label.repaint()

    def end_trial(self):
        """End the trial of 15 subtrials and reset the page. Also write output
        file.
        """
        self.total_duration = time.time() - self.total_duration
        self.next_button.setEnabled(False)
        self.track_button.setEnabled(True)
        self.track_button.setText("Begin Tracking")
        #self.stop_button.setEnabled(False)
        self.text_field.setReadOnly(False)
        self.clicked_dots = []
        self.trial_clicks = self.trial_dictionary[self.trial_id]
        self.clicking_active = False
        trial_duration_string = [format(x * 1000, '.0f') for x in self.trial_durations]
        correct_dots_string = [str(x) for x in self.correct_dots]
        with open('output_file.txt', 'w') as f:
            f.write(self.text_field.text())
            f.write('\n')
            f.write(",".join(trial_duration_string))
            f.write('\n')
            f.write(",".join(correct_dots_string))

    def dot_clicked(self):
        """Updates the information label and the number of clicks left not in that
        order :)
        """
        self.trial_clicks -= 1
        self.update_info_label()
        if self.trial_clicks == 0:
            self.trial_durations.append(time.time() - self.trial_starts[-1])
            for dot in self.dots:
                if (dot.id in self.tracked_dots and
                    dot not in self.clicked_dots):
                    dot.set_color(UNSELECTED_COLOR)
                    self.canvas.draw()
            if self.trial_id == 15:
                self.trial_id = 0
                self.end_trial()
            else:
                self.trial_id += 1
                self.clicked_dots = []
                self.trial_clicks = self.trial_dictionary[self.trial_id]
                self.clicking_active = False
                self.next_button.setEnabled(True)
                #self.stop_button.setEnabled(True)


    def detect_clicked_dot(self, dots_list, event):
        """Uses an events location and returns a mpl.patches object corresponding
        to the click.
        Args:
            dots_list: A list of circle patch objects
            event: The event which triggered the call (contains location)
        Returns:
            circle: mpl.patches.Circle object which was clicked or None
        """
        circle = None
        for dot in dots_list:
            if self._distance(dot.center, (event.xdata, event.ydata)) < dot.radius:
                if circle is not None:
                    if self._distance(dot.center, (event.xdata, event.ydata)) < self._distance(circle.center, (event.xdata, event.ydata)):
                        circle = dot
                else:
                    circle = dot
        return circle

    def onclick(self, event):
        '''When a button is clicked, and while it is being held down it will be a
        different color.
        '''
        self.mouse_pressed = True
        selected_dot = self.detect_clicked_dot(self.dots, event)
        if (selected_dot is not None and
            selected_dot not in self.clicked_dots
            and self.valid_click):
            self.highlighted_dot = selected_dot
            selected_dot.set_color(SELECTION_COLOR)
            self.canvas.draw()




    def onrelease(self, event):
        '''When the button is released, the selection is made if the release
        happens inside of a dot.
        '''

        # TODO, use _distance to determine if highlighted_dot is also an option
        # for clicked dot. if so then click that dot.
        self.mouse_pressed = False
        if (event.xdata is not None):
            selected_dot = self.detect_clicked_dot(self.dots, event)
        else:
            selected_dot = None

        if (self._distance(self.highlighted_dot.center,
                                (event.xdata, event.ydata)) < 0.3):
            selected_dot = self.highlighted_dot
        if (selected_dot is not None
            and selected_dot not in self.clicked_dots
            and self.valid_click):
            if (selected_dot.id in self.tracked_dots):
                self.clicked_dots.append(selected_dot)
                selected_dot.set_color(BLINKING_COLOR)
                self.canvas.draw()
            else:
                self.clicked_dots.append(selected_dot)
                selected_dot.set_color(INCORRECT_COLOR)
                self.correct_dots[self.trial_id] -= 1
                self.canvas.draw()
            self.dot_clicked()
        elif (selected_dot is None
              and self.highlighted_dot is not None
              and self.highlighted_dot not in self.clicked_dots):
            self.highlighted_dot.set_color(COLOR)
            self.canvas.draw()
        self.highlighted_dot = None

    def onmouse(self, event):
        '''If the mouse moves while the user has the cursor pressed the selection should be
        undone and the color should change back.
        '''
        # if (self.mouse_pressed):
        #     if (self.highlighted_dot is not None):
        #         # check to see if dot is still selected
        #         # if not reset the instance variable
        #         # if so do nothing.
        #         if (self.highlighted_dot == self.detect_clicked_dot(self.dots, event)):
        #             pass
        #         else:
        #             self.highlighted_dot.set_color(COLOR)
        #             self.highlighted_dot = None
        #


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
