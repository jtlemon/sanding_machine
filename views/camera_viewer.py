from PySide2 import QtWidgets, QtGui, QtCore


class CameraViewer(QtWidgets.QWidget):
    def __init__(self, camera_index_list=[0]):
        super(CameraViewer, self).__init__()
        self.widget_layout = QtWidgets.QGridLayout(self)
        self.__camera_index_list  = camera_index_list
        self.__camera_lbl_list = [QtWidgets.QLabel() for i in range(len(camera_index_list))]
        for index, camera_lbl in enumerate(self.__camera_lbl_list):
            camera_lbl.setAlignment(QtCore.Qt.AlignCenter)
            camera_lbl.setPixmap(QtGui.QPixmap(u":/icons/icons/icons8-camera-96.png"))
            camera_lbl.setScaledContents(True)
            self.widget_layout.addWidget(camera_lbl, 0, index, 1, 1)
        self.resize_camera_widgets()


    def resizeEvent(self, event:QtGui.QResizeEvent) -> None:
        self.resize_camera_widgets()
        super(CameraViewer, self).resizeEvent(event)

    def resize_camera_widgets(self):
        rec = QtWidgets.QApplication.desktop().screenGeometry()
        width = rec.width()
        total_width = int(width - 300 - (0.3*width))
        total_height = (rec.height() - 200 - 0.2*rec.height())
        width_per_camera = total_width//len(self.__camera_lbl_list)
        # 16 : 9
        # width height
        height_per_camera = int(width_per_camera*9/16)
        for camera_lbl in self.__camera_lbl_list:
            camera_lbl.setMaximumSize(width_per_camera, height_per_camera)

    def new_image_received(self, camera_index, pix_map):
        if camera_index in self.__camera_index_list:
            lbl_index = self.__camera_index_list.index(camera_index)
            self.__camera_lbl_list[lbl_index].setPixmap(pix_map)
