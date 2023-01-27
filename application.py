import sys
from PySide2 import QtCore, QtWidgets, QtGui

# @todo add later to global configurations

APPLICATION_NAME = "Sanding Machine"
APPLICATION_DISP_NAME = "Sanding Machine Controller"
APPLICATION_VERSION = "1.0.0"
APPLICATION_FILE_NAME = "sanding"


class SandingApp(QtWidgets.QApplication):
    # category, color, error_key, error_text
    # category is the text that will be displayed in the error widget main label
    # color is the color of the text in the error widget main label
    # error key is any number if exits this will be displayed in the error dialog
    # error text is the text that will be displayed in the error dialog
    new_message_signal = QtCore.Signal(str, str, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName(APPLICATION_NAME)
        self.setApplicationDisplayName(APPLICATION_DISP_NAME)
        self.setApplicationVersion(APPLICATION_VERSION)
        self.setDesktopFileName(APPLICATION_FILE_NAME)
        self.setDesktopSettingsAware(True)



def get_app() -> SandingApp:
    instance = SandingApp.instance()
    return instance or SandingApp(sys.argv[1:])
