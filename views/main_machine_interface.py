from PySide2 import QtWidgets, QtGui, QtCore

import views.custom_app_widgets as custom_widgets
from configurations import MainConfigurationLoader
from models import MeasureUnitType
from custom_widgets.calculator import Calculator
from custom_widgets.countdown_timer import CountDownTimerManager
from custom_widgets.error_widget import ErrorWidgetLabel
import configurations.static_app_configurations as static_configurations


class MachineInterfaceUi(QtWidgets.QWidget):
    measureUnitChangedSignal = QtCore.Signal(object)

    def __init__(self):
        super(MachineInterfaceUi, self).__init__()
        # create header widget
        self.main_window_layout = QtWidgets.QVBoxLayout()
        self.main_window_layout.setContentsMargins(0, 0, 0, 0)
        self.main_window_layout.setSpacing(0)
        self.header_frame = QtWidgets.QFrame()
        self.header_frame_layout = QtWidgets.QHBoxLayout(self.header_frame)
        self.header_frame_layout.setContentsMargins(0, 0, 10, 0)
        # header widgets
        self.machine_status_lbl = QtWidgets.QLabel()
        self.machine_status_lbl.setText("Ready.....")
        self.machine_status_lbl.setMinimumWidth(200)
        self.header_frame_layout.addWidget(self.machine_status_lbl)

        self.__count_down_timer_widget = CountDownTimerManager.get_widget()
        self.header_frame_layout.addWidget(self.__count_down_timer_widget)
        h_spacer_item_0 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.header_frame_layout.addItem(h_spacer_item_0)
        self.__error_lbl = ErrorWidgetLabel()
        self.__error_lbl.set_error(static_configurations.INSTALLED_ERRORS["machineerror"])
        self.header_frame_layout.addWidget(self.__error_lbl)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.header_frame_layout.addItem(h_spacer_item_1)
        self.header_frame.setObjectName("app_header_frame")
        self.calculator_btn = QtWidgets.QPushButton(self)
        self.header_frame_layout.addWidget(self.calculator_btn)
        self.calculator_btn.setIcon(QtGui.QIcon(':/icons/icons/icons8-calculator-64.png'))
        self.calculator_btn.setIconSize(QtCore.QSize(30, 30))
        self.calculator_btn.setMinimumSize(30, 36)
        self.calculator_btn.setFlat(True)
        self.__weather_icon = QtWidgets.QLabel(self)
        self.__weather_icon.setFixedSize(40, 40)
        self.__weather_icon.setScaledContents(True)
        self.header_frame_layout.addWidget(self.__weather_icon)
        self.__current_temperature_lbl = QtWidgets.QLabel(self)
        self.header_frame_layout.addWidget(self.__current_temperature_lbl)
        self.__current_time_lbl = QtWidgets.QLabel(self)
        self.header_frame_layout.addWidget(self.__current_time_lbl)
        self.main_window_layout.addWidget(self.header_frame, stretch=0)
        self.__app_pages = QtWidgets.QStackedWidget()
        self.main_window_layout.addWidget(self.__app_pages, stretch=1)
        # create footer
        self.footer_frame = QtWidgets.QFrame()
        self.footer_frame.setObjectName("app_footer_frame")
        self.footer_frame_layout = QtWidgets.QHBoxLayout(self.footer_frame)
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)

        self.footer_frame_layout.addItem(h_spacer_item_2)
        self.__inches_btn = custom_widgets.AppFooterButton("inches")
        self.__inches_btn.setCheckable(True)
        self.__inches_btn.setObjectName("main_inches_btn")
        self.__inches_btn.clicked.connect(lambda: self.handle_change_measure_unit(MeasureUnitType.IN_UNIT))
        self.__mm_btn = custom_widgets.AppFooterButton("mm")
        self.__mm_btn.setCheckable(True)
        self.__mm_btn.setObjectName("main_mm_btn")
        self.__mm_btn.clicked.connect(lambda: self.handle_change_measure_unit(MeasureUnitType.MM_UNIT))
        self.footer_frame_layout.addWidget(self.__inches_btn)
        self.footer_frame_layout.addWidget(self.__mm_btn)
        self.main_window_layout.addWidget(self.footer_frame, stretch=0)
        self.setLayout(self.main_window_layout)
        # signals
        self.__footer_buttons = list()
        self.__clock_timer = QtCore.QTimer()
        self.__clock_timer.timeout.connect(self._update_app_clock)
        self.__clock_timer.start(1000)  # update clock every 1sec
        self.calculator_btn.clicked.connect(self._handle_display_calculator)

    def _handle_display_calculator(self):
        self.__calculator = Calculator()
        self.__calculator.show()

    def _update_app_clock(self):
        time = QtCore.QTime.currentTime()
        if MainConfigurationLoader.get_value("time_format") == 24:
            text = time.toString('hh:mm:ss')
        else:
            text = time.toString('hh:mm AP')
        self.__current_time_lbl.setText(text)

    def set_current_temperature(self, new_temp, weather_icon):
        self.__current_temperature_lbl.setText(f"{new_temp}")
        self.__weather_icon.setPixmap(QtGui.QPixmap(":/icons/icons/{}@2x.png".format(weather_icon)))

    def handle_change_measure_unit(self, new_unit: MeasureUnitType):
        if new_unit == MeasureUnitType.IN_UNIT:
            self.__inches_btn.setChecked(True)
            self.__mm_btn.setChecked(False)
        elif new_unit == MeasureUnitType.MM_UNIT:
            self.__inches_btn.setChecked(False)
            self.__mm_btn.setChecked(True)
        else:
            raise ValueError("not implemented")
        MainConfigurationLoader.set_value("measure_unit", new_unit.value, True)
        self.measureUnitChangedSignal.emit(new_unit)

    def add_app_window_widget(self, ref_widget):
        action_button_name = ref_widget.get_footer_btn_name()
        target_page_index = len(self.__footer_buttons)
        action_button = custom_widgets.AppFooterButton(action_button_name, target_page=target_page_index)
        action_button.setCheckable(True)
        action_button.customClickSignal.connect(self.switch_to_another_page)
        self.footer_frame_layout.insertWidget(target_page_index, action_button)
        self.__footer_buttons.append(action_button)
        self.__app_pages.addWidget(ref_widget)

    def switch_to_another_page(self, page_index: int):
        for i in range(len(self.__footer_buttons)):
            btn = self.__footer_buttons[i]
            btn.setChecked(i == page_index)
        self.__app_pages.setCurrentIndex(page_index)

    def get_current_active_widget(self):
        return self.__app_pages.currentWidget()

    def current_page_index(self):
        return self.__app_pages.currentIndex()
