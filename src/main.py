import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, \
                            QLineEdit, QHBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation

from multiprocessing import Process
from threading import Timer
from boundarycollision import BoundaryCollisionDetector
from trackabledot import TrackableDot
import random
import time

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self._define_constants()
        # a figure instance to plot on
        self.figure = Figure(facecolor=self.FACE_COLOR)

        # This is to make the QDialog Window full size.
        if self.START_FULLSCREEN:
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

        # This is used to open and close the app and log the output using the
        # open_close bash script.
        if self.DEBUG_MODE:
            if len(sys.argv) == 2:
                self.argument = float(sys.argv[1])
                t = Timer(self.argument, self.close)
                t.start()

    def _define_constants(self):
        self.FACE_COLOR = 'black'
        self.RADIUS = 0.3
        self.COLOR = 'red'
        self.BLINKING_COLOR = 'green'
        self.START_FULLSCREEN = True
        self.DEBUG_MODE = True
        self.NUMBER_OF_DOTS = 10
        self.NUMBER_OF_TRACK_DOTS = 2
        self.VELOCITY = 3 # in data units / s
        self.BLINKING_DURATION = 2 * 1000 # in ms
        self.TRIAL_DURATION = 17 * 1000 # in ms
        self.INTERVAL = 50 # in ms
        self.TRIAL_ACTIVE = False


    def setup_dots(self):
        """Removes any dots on the canvas and generates a new list of them.
        This method does not draw them or add them to the canvas.
        """
        self.remove_dots()
        for i in range(self.NUMBER_OF_DOTS):
            self.dots.append(TrackableDot((self.generate_location(self.dots, self.RADIUS)), self.RADIUS, self.COLOR, self.generate_velocity(self.VELOCITY), i))

    def draw_dots(self):
        """Uses the dots list and adds the circles to the canvas and draws them.
        This method does not create the circle objects.
        """
        for i in range(len(self.dots)):
            self.ax.add_artist(self.dots[i])
        self.canvas.draw()

    def track_dots(self, num):
        """Sets up a dictionary and in order to start the tracking.
        Args:
            num: an integer less than self.NUMBER_OF_DOTS, this determines the number
            of tracked dots.
        """
        self.tracked_dots = {}
        for i in range(num):
            self.tracked_dots[self.dots[i].id] = (self.dots[i])

    def generate_velocity(self, mag=1.0):
        """ Generate a velocity with magnitude of mag.
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
        self.stop_button = QPushButton('Stop Tracking')
        self.stop_button.clicked.connect(self.stop_tracking_button_clicked)
        self.stop_button.setMaximumWidth(200)

        # text field setup
        self.textField = QLineEdit()
        self.textField.setPlaceholderText("Patient ID")
        self.textField.setMaximumWidth(200)

        # Set up the bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.track_button)
        bottom_layout.addWidget(self.stop_button)
        bottom_layout.addWidget(self.textField)

        # set the whole layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def remove_dots(self):
        """Iterate through the dots array and delete them while removing them
        from the canvas.
        """
        for dot in self.dots:
            dot.remove()
        self.dots = []
        self.canvas.draw()

    def stop_tracking_button_clicked(self, event):
        """Checks to see if tracking is currently active, if it is it stops
        the animation and allows the window to be resized.
        """
        print(self.TRIAL_ACTIVE)
        self.canvas.draw()
        self.track_button.setEnabled(True)
        self.remove_dots()
        try:
            self.line_ani._stop()
        except AttributeError:
            pass

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


    def begin_tracking_button_clicked(self):
        """Action when tracking button clicked.
        Validate the textField.text value and begin the animation sequence.
        """
        self.track_button.setEnabled(False)
        self.grab_default_dimensions()
        self.ax.set_ylim([0, self.HEIGHT])
        self.ax.set_xlim([0, self.WIDTH])
        self.setup_dots()
        self.draw_dots()
        self.canvas.draw()
        self.track_dots(self.NUMBER_OF_TRACK_DOTS)
        # self.animate_blink()
        self.animate_plot()
        self.canvas.draw()
        print(self.TRIAL_ACTIVE)

    def update_dots(self, i):
        detector = BoundaryCollisionDetector(self)
        for dot in self.dots:
            dot.update_position(.05)
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
        num_iter = int(self.TRIAL_DURATION/self.INTERVAL)
        if (i < int(num_iter / self.TRIAL_DURATION * self.BLINKING_DURATION)):
            return True
        else:
            return False

    def conduct_trial(self, i):
        if (self._blink_stage(i)):
            if i == 0:
                print(self.TRIAL_ACTIVE)
                self.TRIAL_ACTIVE = True
                print(self.TRIAL_ACTIVE)
            if i % 6 == 0:
                self.blink_dots(i)
        elif (i + 1 == int(self.TRIAL_DURATION/self.INTERVAL)):
            self.TRIAL_ACTIVE = False
        else:
            self.update_dots(i)


    def animate_plot(self):
        self.dot_ani = animation.FuncAnimation(self.figure, self.conduct_trial, int(self.TRIAL_DURATION/self.INTERVAL), interval=self.INTERVAL, repeat=False)

    def blink_dots(self, i):
        """Uses the dictionary of tracked dots and blinks them.
        """
        for dot in self.tracked_dots.values():
            if dot.color == self.BLINKING_COLOR:
                dot.set_color(self.COLOR)
                dot.color = self.COLOR
            else:
                dot.set_color(self.BLINKING_COLOR)
                dot.color = self.BLINKING_COLOR
            # self.canvas.draw()

    def animate_blink(self):
        self.blink_ani = animation.FuncAnimation(self.figure, self.blink_dots, 9, interval=400, repeat=False)

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
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)


    def _distance(self, loc1, loc2):
        """Outputs distance between two tuples (x, y)
        Args:
            loc1/2: locations for distances to be computed
        Returns:
            dist: float value of distance
        """
        return np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

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
                return dot
        return circle

    def onclick(self, event):
        '''Event handler which prints information about the click.
        '''
        print("click detected")
        selected_dot = self.detect_clicked_dot(self.dots, event)
        if selected_dot != None:
            if(selected_dot.id in self.tracked_dots):
                selected_dot.set_color('green')
                self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
