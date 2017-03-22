import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout

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
START_FULLSCREEN = False
DEBUG_MODE = True

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure(facecolor=FACE_COLOR)

        # This is to make the QDialog Window full size.
        if START_FULLSCREEN:
            self.showMaximized()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # Setup the figure
        self.setup_canvas()

        # Just some button connected to `plot` method
        self.button = QPushButton('Begin Tracking')
        self.button.clicked.connect(self.begin_tracking_button_clicked)
        self.button.setMaximumWidth(200)

        # self.button.clicked.connect(self.plot)
        self.textField = QLineEdit()
        self.textField.setPlaceholderText("Patient ID")
        self.textField.setMaximumWidth(200)

        # Set up the bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.button)
        bottom_layout.addWidget(self.textField)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

        # This is used to open and close the app and log the output using the
        # open_close bash script.
        if DEBUG_MODE:
            if len(sys.argv) == 2:
                self.argument = float(sys.argv[1])
                t = Timer(self.argument, self.close)
                t.start()



    def closeEvent(self, event):
        """This method is called when the application is closing.
        Disconnects the event handler which tracks the clicking.
        """
        print("The window will close.")
        self.figure.canvas.mpl_disconnect(self.cid)
        self.line_ani._stop()
        event.accept()

    def begin_tracking_button_clicked(self):
        """Action when tracking button clicked.
        Validate the textField.text value and begin the animation sequence.
        """
        print(self.minimumSize())
        print(self.maximumSize())
        print(self.textField.text())
        print(self.figure.get_figwidth())
        self.animate_plot()
        self.setFixedSize(self.size())

    def update_line(self, num, data, line):
        line.set_data(data[..., :num])
        return line,

    def animate_plot(self):
        data = np.random.rand(2, 25)
        l, = self.ax.plot([], [], 'r-')
        self.circle = Circle((0.5, 0.5), 1)
        self.ax.add_artist(self.circle)

        self.line_ani = animation.FuncAnimation(self.figure , self.update_line, 25, fargs=(data, l),interval=50, blit=True)

    def setup_canvas(self):
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
