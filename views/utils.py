import os
from PySide2 import QtCore, QtGui
import app_resources_rc

rp = os.path.dirname(os.path.realpath(__file__))
APP_THEME = os.path.join(rp, "..", "assets", "app_style.css")

def load_app_fonts():
    QtGui.QFontDatabase.addApplicationFont(":/fonts/fonts/Helvetica-400.ttf")

def load_app_style():
    with open(APP_THEME) as css_file:
        return css_file.read()
