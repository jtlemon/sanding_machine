from view_managers.joint_profiles_page_manager import JointProfilesPageManager
from PySide2 import QtWidgets
if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    machine_gui_interface = JointProfilesPageManager("Joint Profile")
    machine_gui_interface.showMaximized()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
