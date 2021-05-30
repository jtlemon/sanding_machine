#!/usr/bin/env python3
from PySide2.QtCore import *
from PySide2.QtGui import QMovie
from PySide2.QtWidgets import *


class ImagePlayerDialog(QDialog):
    def __init__(self, filename, parent=None):
        super(ImagePlayerDialog, self).__init__(parent=parent)
        # Load the file into a QMovie
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.movie = QMovie(filename, QByteArray(), self)
        size = self.movie.scaledSize()
        self.movie_screen = QLabel()
        # Make label fit the gif
        self.movie_screen.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.movie_screen.setAlignment(Qt.AlignCenter)

        # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.movie_screen)

        self.setLayout(main_layout)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.__time_out_timer = QTimer()
        self.__time_out_timer.timeout.connect(lambda :self.accept())
        self.__time_out_timer.setSingleShot(True)
        self.__time_out_timer.start(2000)
        self.movie.start()
        self.setMinimumSize(500, 500)

