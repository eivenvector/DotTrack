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

from threading import Timer

import random

FACE_COLOR = 'black'
START_FULLSCREEN = True
DEBUG_MODE = True
NUMBER_OF_DOTS = 10

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure(facecolor=FACE_COLOR)

        # This is to make the QDialog Window full size.
        if START_FULLSCREEN:
            self.showMaximized()
            


        self.canvas = FigureCanvas(self.figure)

        # Steup the figures axis, margins, and background color.
        self.setup_figure()

        # setup the gui
        self.setup_ui()

        # This is used to open and close the app and log the output using the
        # open_close bash script.
        if DEBUG_MODE:
            if len(sys.argv) == 2:
                self.argument = float(sys.argv[1])
                t = Timer(self.argument, self.close)
                t.start()

    def setup_dots(self):
        self.dots = []
        radius = 0.3
        for i in range(NUMBER_OF_DOTS):
            self.dots.append(Circle((self.generate_location()), radius, color='red'))

    def draw_dots(self):
        for i in range(len(self.dots)):
            self.ax.add_artist(self.dots[i])
        self.canvas.draw()

    def generate_location(self):
        """Generates a location using the width and height of the window.
        Returns:
            a tuple which represents the location.
        """

        return (np.random.uniform(0.1, 0.9) * self.WIDTH, np.random.uniform(0.1, 0.9) * self.HEIGHT)

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

    def stop_tracking_button_clicked(self, event):
        """Checks to see if tracking is currently active, if it is it stops
        the animation and allows the window to be resized.
        """
        self.reset_sizing()
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
        print("width: %f, height: %f" % (self.WIDTH, self.HEIGHT))


    def begin_tracking_button_clicked(self):
        """Action when tracking button clicked.
        Validate the textField.text value and begin the animation sequence.
        """
        self.grab_default_dimensions()
        self.ax.set_ylim([0, self.HEIGHT])
        self.ax.set_xlim([0, self.WIDTH])
        self.setup_dots()
        self.draw_dots()

    def update_line(self, num, data, line):
        line.set_data(data[..., :num])
        return line,

    def animate_plot(self):
        data = np.random.rand(2, 25)
        l, = self.ax.plot([], [], 'r-')
        self.circle = Circle((0.5, 0.5), 1)
        self.ax.add_artist(self.circle)

        self.line_ani = animation.FuncAnimation(self.figure , self.update_line, 25, fargs=(data, l),interval=50, blit=True)

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

    def onclick(self, event):
        '''Event handler which prints information about the click.
        '''
        print("click detected")
        print(event.x)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
