from PySide2 import QtWidgets, QtCore


class CountDownTimerWidget(QtWidgets.QLabel):
    def __init__(self):
        super(CountDownTimerWidget, self).__init__()
        self.__time_out_value = 0
        self.__remaining_time = 0
        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self._sec_passed)

    def start(self, timeout):
        self.__time_out_value = timeout
        self.__remaining_time = timeout
        self.update_display()
        self.__timer.start(1000) # make tick every sec

    def _sec_passed(self):
        self.__remaining_time = self.__remaining_time - 1
        self.update_display()
        if self.__remaining_time <= 0:
            self.stop()

    def stop(self):
        self.__timer.stop()

    def clear(self):
        self.__remaining_time = 0
        self.update_display()

    def update_display(self):
        hours = int(self.__remaining_time / 3600)
        min = int((self.__remaining_time % 3600) / 60)
        sec = (self.__remaining_time % 60)
        txt = " timer :%02d:%02d:%02d" % (hours, min, sec)
        self.setText(txt)


class CountDownTimerManager:
    __timer_widget = None
    @staticmethod
    def create_widget():
        if CountDownTimerManager.__timer_widget is None:
            CountDownTimerManager.__timer_widget = CountDownTimerWidget()

    @staticmethod
    def start(timeout):
        if CountDownTimerManager.__timer_widget:
            CountDownTimerManager.__timer_widget.start(timeout)

    @staticmethod
    def stop():
        if CountDownTimerManager.__timer_widget:
            CountDownTimerManager.__timer_widget.stop()

    @staticmethod
    def clear():
        if CountDownTimerManager.__timer_widget:
            CountDownTimerManager.__timer_widget.clear()

    @staticmethod
    def get_widget():
        CountDownTimerManager.create_widget()
        CountDownTimerManager.__timer_widget.clear()
        return CountDownTimerManager.__timer_widget










