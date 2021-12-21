import cv2
from PySide2 import QtWidgets, QtCore, QtGui
from views.custom_app_widgets import ProfileComboBox

class SandingCameraWidget(QtWidgets.QLabel):
    newAreaSelectedSignal = QtCore.Signal(QtCore.QRect)
    def __init__(self, parent = None):
        super(SandingCameraWidget, self).__init__(parent=parent)
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()
        self.workplace_area = None
        self.part_area = None
        self.is_annotation_enabled = False

    def set_work_place_area(self, area:QtCore.QRect):
        self.workplace_area = area

    def set_part_area(self, area:QtCore.QRect):
        self.part_area = area

    def set_image(self, pix_map):
        if self.workplace_area is not None:
            self.draw_rectangles(pix_map, self.workplace_area, QtCore.Qt.blue)
        if self.part_area is not None:
            self.draw_rectangles(pix_map, self.part_area, QtCore.Qt.red)
        self.setPixmap(pix_map)

    def draw_rectangles(self, pix_map, rect:QtCore.QRect, color):
        # create painter instance with pixmap
        painter= QtGui.QPainter(pix_map)
        pen_rectangle = QtGui.QPen(color)
        pen_rectangle.setWidth(3)
        painter.setPen(pen_rectangle)
        painter.drawRect(rect.x(), rect.y(), rect.width(), rect.height())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.is_annotation_enabled:
                self.origin = QtCore.QPoint(event.pos())
                self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
                self.rubberBand.show()


    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.rubberBand.hide()
            self.newAreaSelectedSignal.emit(self.rubberBand.geometry())

    def enable_annotation(self, is_enabled):
        self.is_annotation_enabled = is_enabled

class TestImageSource(QtCore.QThread):
    newImageSignal  = QtCore.Signal(QtGui.QPixmap)
    def run(self) -> None:
        cam = cv2.VideoCapture(0)
        while cam.isOpened():
            ret, image = cam.read()
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QtGui.QImage(image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            pix_map = QtGui.QPixmap.fromImage(q_image)
            self.newImageSignal.emit(pix_map)
            cv2.waitKey(100)


class SandingPageView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SandingPageView, self).__init__(parent=parent)
        self.widget_layout = QtWidgets.QVBoxLayout(self)

        # header section
        self.header_frame = QtWidgets.QFrame()
        self.header_frame_layout = QtWidgets.QHBoxLayout(self.header_frame)
        self.header_frame_layout.addWidget(QtWidgets.QLabel("DOOR STYLE"))
        self.door_styles_combo = ProfileComboBox(self.header_frame)
        self.door_styles_combo.setMinimumSize(350,60)
        self.header_frame_layout.addWidget(self.door_styles_combo)
        self.header_frame_layout.addStretch(1)
        self.header_frame_layout.addWidget(QtWidgets.QLabel("SANDING PROGRAM"))
        self.sanding_programs_combo = ProfileComboBox(self.header_frame)
        self.sanding_programs_combo.setMinimumSize(350, 60)
        self.header_frame_layout.addWidget(self.sanding_programs_combo)

        # camera section
        self.camera_frame_layout_wrapper = QtWidgets.QHBoxLayout()
        self.camera_frame = QtWidgets.QFrame()
        self.camera_frame_layout = QtWidgets.QVBoxLayout(self.camera_frame)
        self.camera_frame_layout.addStretch(1)
        self.camera_frame_header_layout = QtWidgets.QHBoxLayout()
        self.localize_part_btn = QtWidgets.QPushButton("Annotate Part")
        self.localize_part_btn.setCheckable(True)
        self.localize_workplace_btn = QtWidgets.QPushButton("Annotate Workplace")
        self.localize_workplace_btn.setCheckable(True)
        self.camera_frame_header_layout.addWidget(self.localize_part_btn)
        self.camera_frame_header_layout.addStretch(1)
        self.camera_frame_header_layout.addWidget(self.localize_workplace_btn)
        self.camera_frame_layout.addLayout(self.camera_frame_header_layout)
        self.camera_widget = SandingCameraWidget()
        self.camera_frame_layout.addWidget(self.camera_widget)
        self.camera_frame_layout_wrapper.addStretch(1)
        self.camera_frame_layout_wrapper.addWidget(self.camera_frame)
        self.camera_frame_layout_wrapper.addStretch(1)
        # footer section
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setFixedSize(200, 60)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setFixedSize(200, 60)
        self.footer_layout.addStretch(1)
        self.footer_layout.addWidget(self.start_btn)
        self.footer_layout.addWidget(self.cancel_btn)
        self.footer_layout.addStretch(1)
        # add all ele
        self.widget_layout.addWidget(self.header_frame)
        self.widget_layout.addLayout(self.camera_frame_layout_wrapper)
        self.widget_layout.addLayout(self.footer_layout)


class SandingPageViewManager(SandingPageView):
    def __init__(self, parent=None):
        super(SandingPageViewManager, self).__init__(parent= parent)
        self.camera_widget.newAreaSelectedSignal.connect(self._handle_image_area_selected)
        self.localize_part_btn.clicked.connect(lambda state : self.camera_widget.enable_annotation(state))
        self.localize_workplace_btn.clicked.connect(lambda state: self.camera_widget.enable_annotation(state))

    def _handle_image_area_selected(self, rect:QtCore.QRect):
        if self.localize_workplace_btn.isChecked():
            self.camera_widget.set_work_place_area(rect)
        elif self.localize_part_btn.isChecked():
            self.camera_widget.set_part_area(rect)
        self.localize_workplace_btn.setChecked(False)
        self.localize_part_btn.setChecked(False)
        self.camera_widget.enable_annotation(False)



if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    app.setStyleSheet(utils.load_app_style())
    sanding_camera = SandingPageViewManager()
    sanding_camera.show()
    image_source = TestImageSource()
    image_source.newImageSignal.connect(lambda pixmap: sanding_camera.camera_widget.set_image(pixmap))
    image_source.start()
    app.exec_()

