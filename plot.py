import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def setup_figure():
    '''Set up figure to eliminate the toolbar and resizing.
    Presents the figure.
    '''
    # Remove toolbar
    mpl.rcParams['toolbar'] = 'None'
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Remove ticks and labels on axis
    ax.set_xticks([])
    ax.set_yticks([])
    # Remove margin on plot.
    plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.00)
    # Set the color of the axis
    ax.set_facecolor('black')
    return fig, ax

def onclick(event):
    '''Event handler which prints information about the click.
    '''
    print("click detected")
    print(event.x)

def setup_click_handler(fig):
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

if __name__ == '__main__':
    fig, ax = setup_figure()
    setup_click_handler(fig)
    plt.show()
