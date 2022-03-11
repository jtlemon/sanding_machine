from PySide2 import QtWidgets

from custom_widgets.spin_box import CustomSpinBox
from views.generated import Ui_SandingProgramCreationDialog


class SandingProgramCreationDialog(QtWidgets.QDialog, Ui_SandingProgramCreationDialog):
    def __init__(self, speed_spinbox_range=(0.1, 5, 0.2, 1),  # min, max, step, initial
                 pressure_spinbox_range=(0.1, 5, 0.2, 1),  # min, max, step, initial
                 parent=None):
        super(SandingProgramCreationDialog, self).__init__(parent=parent)
        self.setupUi(self)

        self.overlap_spinbox = CustomSpinBox(0, 100, 10, 0,
                                             extra="%",
                                             allow_mode_change=False,
                                             numpad_title="overlap",
                                             disp_precession=0,

                                             )
        self.custom_prams_grid.addWidget(self.overlap_spinbox, 0, 1, 1, 1)

        self.pressure_spinbox = CustomSpinBox(0, 100, 1, 0,
                                              extra="",
                                              allow_mode_change=False,
                                              numpad_title="pressure",
                                              disp_precession=0,

                                              )
        self.custom_prams_grid.addWidget(self.pressure_spinbox, 1, 1, 1, 1)
        self.speed_spinbox = CustomSpinBox(10, 100, 10, 10,
                                           extra="%",
                                           allow_mode_change=False,
                                           numpad_title="Speed",
                                           disp_precession=0,
                                           )
        self.custom_prams_grid.addWidget(self.speed_spinbox, 2, 1, 1, 1)

        self.hangover_spinbox = CustomSpinBox(0, 40, 5, 0,
                                              extra="%",
                                              allow_mode_change=False,
                                              numpad_title="overhang",
                                              disp_precession=0,
                                              )
        self.custom_prams_grid.addWidget(self.hangover_spinbox, 3, 1, 1, 1)


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    app.setStyleSheet(utils.load_app_style())
    window = SandingProgramCreationDialog()
    window.exec_()
