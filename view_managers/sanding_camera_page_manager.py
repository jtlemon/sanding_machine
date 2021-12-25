import cv2
from PySide2 import QtWidgets, QtCore, QtGui
from views.custom_app_widgets import ProfileComboBox
from configurations.system_configuration_loader import MainConfigurationLoader
from models import MeasureUnitType
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger


class SandingCameraWidget(QtWidgets.QLabel):
    newAreaSelectedSignal = QtCore.Signal(QtCore.QRect)
    def __init__(self, parent = None):
        super(SandingCameraWidget, self).__init__(parent=parent)
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()
        self.workplace_area = None
        self.part_area = None
        self.is_annotation_enabled = True
        #self.setScaledContents(True)

    def set_work_place_area(self, area:QtCore.QRect):
        self.workplace_area = area
        MainConfigurationLoader.set_value("workspace_points",
                                          [area.x(), area.y(), area.width(), area.height()],
                                          auto_store=True)

    def set_part_area(self, area:QtCore.QRect):
        self.part_area = area

    def clr_part_area(self):
        self.part_area = None

    def set_image(self, pix_map):
        if self.workplace_area is not None:
            self.draw_rect(pix_map, self.workplace_area, QtCore.Qt.blue)
        if self.part_area is not None:
            self.draw_rect(pix_map, self.part_area, QtCore.Qt.green)
        self.setPixmap(pix_map)

    def draw_rect(self, pix_map, rect: QtCore.QRect, color):
        painter = QtGui.QPainter(pix_map)
        pen_rectangle = QtGui.QPen(color)
        pen_rectangle.setWidth(3)
        painter.setPen(pen_rectangle)
        painter.drawRect(rect)



    def draw_rectangles(self, pix_map, rect:QtCore.QRect, color):
        # create painter instance with pixmap
        painter= QtGui.QPainter(pix_map)
        path = QtGui.QPainterPath()
        path.addRect(rect)

        pen_rectangle = QtGui.QPen(QtCore.Qt.black)
        pen_rectangle.setWidth(3)
        painter.setPen(pen_rectangle)
        painter.fillPath(path, QtCore.Qt.red)
        painter.drawPath(path)
        # new sec
        path = QtGui.QPainterPath()
        path.addRect(rect)
        internal_rect = QtCore.QRect(
            rect.x() + 20,
            rect.y() + 20,
            rect.width() - 40,
            rect.height() - 40,
        )
        path.addRect(internal_rect)
        painter.fillPath(path, QtCore.Qt.red)
        painter.drawPath(path)



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
        self.widget_layout = QtWidgets.QHBoxLayout(self)

        # header section
        self.header_frame = QtWidgets.QFrame()
        self.header_frame_layout = QtWidgets.QVBoxLayout(self.header_frame)
        self.header_frame_layout.addWidget(QtWidgets.QLabel("DOOR STYLE"))
        self.door_styles_combo = ProfileComboBox(self.header_frame)
        self.door_styles_combo.setFixedSize(350,60)
        self.header_frame_layout.addWidget(self.door_styles_combo)
        self.header_frame_layout.addWidget(QtWidgets.QLabel("SANDING PROGRAM"))
        self.sanding_programs_combo = ProfileComboBox(self.header_frame)
        self.sanding_programs_combo.setFixedSize(350, 60)
        self.header_frame_layout.addWidget(self.sanding_programs_combo)
        self.header_frame_layout.addStretch(1)
        # footer section
        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setFixedHeight(60)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(60)
        self.header_frame_layout.addWidget(self.start_btn)
        self.header_frame_layout.addWidget(self.cancel_btn)

        # camera section
        self.camera_frame_layout_wrapper = QtWidgets.QHBoxLayout()
        self.camera_frame = QtWidgets.QFrame()
        self.camera_frame_layout = QtWidgets.QVBoxLayout(self.camera_frame)
        self.camera_frame_layout.addStretch(1)
        self.camera_frame_header_layout = QtWidgets.QHBoxLayout()
        self.localize_part_btn = QtWidgets.QPushButton("Part")
        self.localize_part_btn.setFixedSize(200, 60)
        self.localize_part_btn.setCheckable(True)
        self.localize_workplace_btn = QtWidgets.QPushButton("  Workplace  ")
        self.localize_workplace_btn.setFixedSize(200, 60)
        self.localize_workplace_btn.setCheckable(True)
        self.camera_frame_header_layout.addWidget(self.localize_part_btn)
        self.camera_frame_header_layout.addStretch(1)
        self.camera_frame_header_layout.addWidget(QtWidgets.QLabel("Annotate"))
        self.camera_frame_header_layout.addStretch(1)
        self.camera_frame_header_layout.addWidget(self.localize_workplace_btn)
        self.camera_frame_layout.addLayout(self.camera_frame_header_layout)
        self.camera_widget = SandingCameraWidget()
        self.camera_frame_layout.addWidget(self.camera_widget)
        self.camera_frame_layout_wrapper.addStretch(1)
        self.camera_frame_layout_wrapper.addWidget(self.camera_frame)
        self.camera_frame_layout_wrapper.addStretch(1)

        # add all ele
        self.widget_layout.addWidget(self.header_frame)
        self.widget_layout.addStretch(1)
        self.widget_layout.addLayout(self.camera_frame_layout_wrapper)


class SandingPageViewManager(SandingPageView, AbstractOperationWidgetManger):
    def __init__(self, footer_btn="Camera", parent=None):
        super(SandingPageViewManager, self).__init__(parent= parent)
        self.__footer_btn_text = footer_btn
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

    def new_image_received(self, cam_index:int, pix_map:QtGui.QPixmap):
        if cam_index == 0:
            self.camera_widget.set_image(pix_map)

    def change_measure_mode(self, unit: MeasureUnitType):
        pass


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False


    def handle_joint_dowel_profile_updated(self, new_profiles):
        pass

    def handle_setting_changed(self):
        pass

    def change_measure_mode(self, unit: MeasureUnitType):
        pass



class ModifiedSandingPageView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModifiedSandingPageView, self).__init__(parent)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.main_widget_frame = QtWidgets.QFrame()
        self.main_widget_frame_layout = QtWidgets.QVBoxLayout(self.main_widget_frame)
        self.top_h_layout = QtWidgets.QHBoxLayout()
        self.door_styles_combo = ProfileComboBox(self)
        self.door_styles_combo.setFixedSize(350, 60)
        self.top_h_layout.addWidget(QtWidgets.QLabel("Door Style"))
        self.top_h_layout.addWidget(self.door_styles_combo)
        self.top_h_layout.addStretch(1)
        self.sanding_programs_combo = ProfileComboBox(self)
        self.sanding_programs_combo.setFixedSize(350, 60)
        self.top_h_layout.addWidget(QtWidgets.QLabel("Sanding Program"))
        self.top_h_layout.addWidget(self.sanding_programs_combo)
        self.main_widget_frame_layout.addLayout(self.top_h_layout, stretch=0)
        self.main_widget_frame_layout.addStretch(1)
        ########################
        # validator = QRegExpValidator(QRegExp(r'[0-9].+'))
        self.float_validator = QtGui.QDoubleValidator(0, 10000, 2)
        self.camera_frame = QtWidgets.QFrame()
        self.camera_frame_layout = QtWidgets.QHBoxLayout(self.camera_frame)
        # left width
        self.localize_part_btn = QtWidgets.QPushButton("Part")
        self.localize_part_btn.setFixedHeight(60)
        self.localize_part_btn.setCheckable(True)

        self.left_side_cam_frame =  QtWidgets.QFrame()
        self.left_side_cam_frame_layout = QtWidgets.QVBoxLayout(self.left_side_cam_frame)
        self.left_side_cam_frame_layout.addWidget(self.localize_part_btn)
        self.left_side_cam_frame_layout.addStretch(1)
        self.left_side_cam_frame_layout.addWidget(QtWidgets.QLabel("Width(mm)"))
        self.part_width = QtWidgets.QLineEdit()
        self.part_width.setValidator(self.float_validator)
        self.left_side_cam_frame_layout.addWidget(self.part_width)
        self.left_side_cam_frame_layout.addStretch(1)
        self.camera_frame_layout.addWidget(self.left_side_cam_frame, stretch=0)
        #  center
        self.center_side_cam_frame = QtWidgets.QFrame()
        self.center_side_cam_frame_layout = QtWidgets.QVBoxLayout(self.center_side_cam_frame)
        self.camera_widget = SandingCameraWidget()
        self.center_side_cam_frame_layout.addWidget(self.camera_widget, stretch=1)
        self.camera_frame_layout.addWidget(self.center_side_cam_frame, stretch=1)
        self.center_footer_layout = QtWidgets.QHBoxLayout()
        self.center_footer_layout.addWidget(QtWidgets.QLabel("Length(mm)"))
        self.part_length_lin = QtWidgets.QLineEdit()
        self.part_length_lin.setValidator(self.float_validator)
        self.center_footer_layout.addWidget(self.part_length_lin)
        self.center_footer_layout.addStretch(1)
        self.center_footer_layout.addWidget(QtWidgets.QLabel("Length(mm)"))
        self.workspace_length_lin = QtWidgets.QLineEdit()
        self.workspace_length_lin.setValidator(self.float_validator)
        self.center_footer_layout.addWidget(self.workspace_length_lin)
        self.center_side_cam_frame_layout.addLayout(self.center_footer_layout, stretch=0)
        self.center_side_cam_frame.setFixedWidth(640)
        # right width
        self.right_side_cam_frame = QtWidgets.QFrame()
        self.right_side_cam_frame_layout = QtWidgets.QVBoxLayout(self.right_side_cam_frame)
        self.localize_workplace_btn = QtWidgets.QPushButton("  Workplace  ")
        self.localize_workplace_btn.setFixedHeight(60)
        self.localize_workplace_btn.setCheckable(True)
        self.right_side_cam_frame_layout.addWidget(self.localize_workplace_btn)
        self.right_side_cam_frame_layout.addStretch(1)
        self.right_side_cam_frame_layout.addWidget(QtWidgets.QLabel("Width(mm)"))
        self.workspace_width = QtWidgets.QLineEdit()
        self.workspace_width.setValidator(self.float_validator)
        self.right_side_cam_frame_layout.addWidget(self.workspace_width)
        self.right_side_cam_frame_layout.addStretch(1)
        self.camera_frame_layout.addWidget(self.right_side_cam_frame, stretch=0)
        self.localize_part_btn.setVisible(False)
        self.localize_workplace_btn.setVisible(False)
        self.main_widget_frame_layout.addWidget(self.camera_frame)

        # connect all
        self.widget_layout.addStretch(1)
        self.widget_layout.addWidget(self.main_widget_frame)
        self.widget_layout.addStretch(1)
        self.camera_widget.setFixedSize(640, 480)


class ModifiedSandingPageManager(ModifiedSandingPageView):
    def __init__(self, footer_btn="Camera", parent= None):
        super(ModifiedSandingPageManager, self).__init__(parent=parent)
        self.__footer_btn_text = footer_btn
        self.camera_widget.newAreaSelectedSignal.connect(self._handle_image_area_selected)

    def new_image_received(self, cam_index:int, pix_map:QtGui.QPixmap):
        if cam_index == 0:
            rect = self.get_part_rect()
            if rect is not None:
                self.camera_widget.draw_rectangles(pix_map, rect, QtCore.Qt.darkGreen)
            self.camera_widget.set_image(pix_map)

    def get_part_rect(self):
        part_width_str = self.part_width.text()
        part_length_str = self.part_length_lin.text()
        workspace_width_str = self.workspace_width.text()
        workspace_length_str = self.workspace_length_lin.text()
        if len(part_width_str) > 0 and len(part_length_str) and\
            len(workspace_width_str) > 0 and len(workspace_length_str):
            part_width = float(part_width_str)
            part_length = float(part_length_str)
            workspace_width = float(workspace_width_str)
            workspace_length= float(workspace_length_str)
            part_width_pixcels = int((part_width/workspace_width)*self.camera_widget.height())
            part_length_pixels = int((part_length/workspace_length)*self.camera_widget.width())
            generated_rect = QtCore.QRect(0, self.camera_widget.height() - part_width_pixcels,
                                 part_length_pixels, part_width_pixcels)
            return  generated_rect

    def _handle_image_area_selected(self, rect:QtCore.QRect):
        if self.localize_workplace_btn.isChecked():
            self.camera_widget.set_work_place_area(rect)
        elif self.localize_part_btn.isChecked():
            self.camera_widget.set_part_area(rect)
        self.localize_workplace_btn.setChecked(False)
        self.localize_part_btn.setChecked(False)
        self.camera_widget.enable_annotation(False)

    def _handle_image_area_selected(self, rect:QtCore.QRect):
        if self.localize_workplace_btn.isChecked():
            self.camera_widget.set_work_place_area(rect)
        elif self.localize_part_btn.isChecked():
            self.camera_widget.set_part_area(rect)
        self.localize_workplace_btn.setChecked(False)
        self.localize_part_btn.setChecked(False)
        self.camera_widget.enable_annotation(False)


    def change_measure_mode(self, unit: MeasureUnitType):
        pass


    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False


    def handle_joint_dowel_profile_updated(self, new_profiles):
        pass

    def handle_setting_changed(self):
        pass

    def change_measure_mode(self, unit: MeasureUnitType):
        pass


if __name__ == "__main__":
    from views import utils
    app = QtWidgets.QApplication([])
    utils.load_app_fonts()
    app.setStyleSheet(utils.load_app_style())
    sanding_camera = ModifiedSandingPageManager()
    sanding_camera.show()
    image_source = TestImageSource()
    image_source.newImageSignal.connect(lambda pixmap: sanding_camera.new_image_received(0, pixmap))
    image_source.start()
    sanding_camera.part_width.setText("200")
    sanding_camera.part_length_lin.setText("200")
    sanding_camera.workspace_width.setText("400")
    sanding_camera.workspace_length_lin.setText("800")
    app.exec_()

