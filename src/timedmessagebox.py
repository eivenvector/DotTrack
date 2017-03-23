from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer

class TimedMessageBox(QMessageBox):
    # inspired by: http://stackoverflow.com/questions/23480334/timed-qmessagebox
    def __init__(self, duration, message):
        super(TimedMessageBox, self).__init__()
        self.timeout = duration
        timeoutMessage = "Beginning task in {} seconds".format(duration)
        self.setText('\n'.join((message, timeoutMessage)))

    def showEvent(self, event):
        QTimer().singleShot(self.timeout*1000, self.close)
        super(TimedMessageBox, self).showEvent(event)
