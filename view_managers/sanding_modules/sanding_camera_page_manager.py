import cv2
from PySide2 import QtWidgets, QtCore, QtGui
from views.custom_app_widgets import ProfileComboBox
from configurations.system_configuration_loader import MainConfigurationLoader
from models import MeasureUnitType
from view_managers.abs_operation_widget_manager import AbstractOperationWidgetManger
from functools import partial
from models.get_part_from_tld import getParts


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
        self.setFixedSize(1300, 650)

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




class ModifiedSandingPageView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModifiedSandingPageView, self).__init__(parent)
        self.part_getter = getParts()
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_layout.setContentsMargins(15, 15, 15, 15)
        self.main_widget_frame = QtWidgets.QFrame()
        self.main_widget_frame_layout = QtWidgets.QVBoxLayout(self.main_widget_frame)
        self.top_h_layout = QtWidgets.QHBoxLayout()
        self.door_styles_combo = ProfileComboBox(self)
        self.door_styles_combo.setFixedSize(350, 60)
        self.top_h_layout.addWidget(QtWidgets.QLabel("Door Style"))
        self.top_h_layout.addWidget(self.door_styles_combo)
        self.top_h_layout.addStretch(1)
        self.probing_option = QtWidgets.QCheckBox("Probing")
        # self.top_h_layout.addWidget(self.probing_option)
        self.probing_option.setChecked(False)
        self.l_r_process = QtWidgets.QCheckBox("Left>Right Process")
        self.top_h_layout.addWidget(self.l_r_process)
        self.top_h_layout.addStretch(1)
        self.sanding_programs_combo = ProfileComboBox(self)
        self.sanding_programs_combo.setFixedSize(350, 60)
        self.top_h_layout.addWidget(QtWidgets.QLabel("Sanding Program"))
        self.top_h_layout.addWidget(self.sanding_programs_combo)
        self.main_widget_frame_layout.addLayout(self.top_h_layout, stretch=0)
        self.main_widget_frame_layout.addStretch(1)


        # Added radio buttons for Part placement by Bhavin on 1/16/23

        self.part_placement_layout = QtWidgets.QHBoxLayout(self)
        self.part_placement_layout.addWidget(QtWidgets.QLabel("Part Placement:"))
        self.part_placement_group = QtWidgets.QButtonGroup(self) # Number group
        
        self.normal_placement_button = QtWidgets.QRadioButton("Normal",self)
        self.normal_placement_button.setChecked(True)
        # self.normal_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.normal_placement_button,0)
        self.part_placement_layout.addWidget(self.normal_placement_button)

        self.rotate_plus_90_placement_button = QtWidgets.QRadioButton("Rotate +90°",self)
        # self.rotate_plus_90_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.rotate_plus_90_placement_button,1)
        self.part_placement_layout.addWidget(self.rotate_plus_90_placement_button)

        self.rotate_minus_90_placement_button = QtWidgets.QRadioButton("Rotate -90°",self)
        # self.rotate_minus_90_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.rotate_minus_90_placement_button,2)
        self.part_placement_layout.addWidget(self.rotate_minus_90_placement_button)

        self.rotate_180_placement_button = QtWidgets.QRadioButton("Rotate 180°",self)
        # self.rotate_180_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.rotate_180_placement_button,3)
        self.part_placement_layout.addWidget(self.rotate_180_placement_button)

        self.flipped_placement_button = QtWidgets.QRadioButton("Flipped",self)
        # self.flipped_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.flipped_placement_button,4)
        self.part_placement_layout.addWidget(self.flipped_placement_button)

        self.mirrored_placement_button = QtWidgets.QRadioButton("Mirrored",self)
        # self.mirrored_placement_button.clicked.connect(self.handle_length_and_width)
        
        self.part_placement_group.addButton(self.mirrored_placement_button,5)
        self.part_placement_layout.addWidget(self.mirrored_placement_button)



        
        


        self.main_widget_frame_layout.addLayout(self.part_placement_layout, stretch=0)
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

        self.right_cancel_button = QtWidgets.QPushButton("Cancel")
        self.right_cancel_button.setMinimumSize(200, 60)
        self.left_side_cam_frame = QtWidgets.QFrame()
        self.left_side_cam_frame_layout = QtWidgets.QVBoxLayout(self.left_side_cam_frame)
        self.left_side_cam_frame_layout.setSpacing(15)
        self.left_side_cam_frame_layout.addWidget(self.localize_part_btn)
        self.start_left_button = QtWidgets.QPushButton("Start Left")
        self.start_left_button.setMinimumSize(200, 60)
        self.left_slab_option = QtWidgets.QCheckBox("5 piece")
        self.left_side_cam_frame_layout.addWidget(self.start_left_button)
        self.left_side_cam_frame_layout.addWidget(self.right_cancel_button)
        self.left_side_cam_frame_layout.addWidget(self.left_slab_option)
        self.left_side_cam_frame_layout.addStretch(1)
        self.part_width_label = QtWidgets.QLabel("Width(in)")
        self.left_side_cam_frame_layout.addWidget(self.part_width_label)
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
        
        #Adding move right and left buttons (Bhavin 1/16/2023)
        self.current_work_zone = 'left'
        self.move_to_right_work_zone_button = QtWidgets.QPushButton('Move right',self)
        self.move_to_left_work_zone_button = QtWidgets.QPushButton('Move left',self)
        self.move_to_left_work_zone_button.setDisabled(True)

        self.move_to_right_work_zone_button.clicked.connect(partial(self.move_workspace_to,'right'))
        self.move_to_left_work_zone_button.clicked.connect(partial(self.move_workspace_to,'left'))

        self.center_footer_layout.addWidget(self.move_to_right_work_zone_button)
        self.center_footer_layout.addStretch(1)
        self.part_length_label = QtWidgets.QLabel("Length(in)")
        self.center_footer_layout.addWidget(self.part_length_label)
        self.part_length_lin = QtWidgets.QLineEdit()
        self.part_length_lin.setValidator(self.float_validator)
        

        self.center_footer_layout.addWidget(self.part_length_lin)
        self.center_footer_layout.addStretch(1)
        self.qr_scan_line = QtWidgets.QLineEdit()
        self.qr_scan_line.setPlaceholderText("QR Code")
        self.center_footer_layout.addWidget(self.qr_scan_line)
        self.center_footer_layout.addStretch(1)
        self.workspace_length_label = QtWidgets.QLabel("Length(in)")
        self.center_footer_layout.addWidget(self.workspace_length_label)
        self.workspace_length_lin = QtWidgets.QLineEdit()
        self.workspace_length_lin.setValidator(self.float_validator)
        self.center_footer_layout.addWidget(self.workspace_length_lin)

        self.center_footer_layout.addWidget(self.move_to_left_work_zone_button)
        self.center_footer_layout.addStretch(1)

        self.center_side_cam_frame_layout.addLayout(self.center_footer_layout, stretch=0)

        # right width
        self.right_side_cam_frame = QtWidgets.QFrame()
        self.right_side_cam_frame_layout = QtWidgets.QVBoxLayout(self.right_side_cam_frame)
        self.right_side_cam_frame_layout.setSpacing(15)
        self.localize_workplace_btn = QtWidgets.QPushButton("  Workplace  ")
        self.localize_workplace_btn.setFixedHeight(60)
        self.localize_workplace_btn.setCheckable(True)
        self.right_side_cam_frame_layout.addWidget(self.localize_workplace_btn)
        self.start_right_button = QtWidgets.QPushButton("Start Right")
        self.start_right_button.setMinimumSize(200, 60)
        self.right_slab_option = QtWidgets.QCheckBox("5 piece")
        self.right_side_cam_frame_layout.addWidget(self.start_right_button)
        self.right_side_cam_frame_layout.addWidget(self.right_cancel_button)
        self.right_side_cam_frame_layout.addWidget(self.right_slab_option)

        self.right_side_cam_frame_layout.addStretch(1)
        self.workspace_width_label = QtWidgets.QLabel("Width(in)")
        self.right_side_cam_frame_layout.addWidget(self.workspace_width_label)
        self.workspace_width = QtWidgets.QLineEdit()
        self.workspace_width.setValidator(self.float_validator)
        self.right_side_cam_frame_layout.addWidget(self.workspace_width)
        self.right_side_cam_frame_layout.addStretch(1)
        self.camera_frame_layout.addWidget(self.right_side_cam_frame, stretch=0)
        self.localize_part_btn.setVisible(False)
        self.localize_workplace_btn.setVisible(False)
        self.main_widget_frame_layout.addWidget(self.camera_frame)

        # connect all
        #self.widget_layout.addStretch(1)
        self.widget_layout.addWidget(self.main_widget_frame)
        #self.widget_layout.addStretch(1)
        #self.camera_widget.setMinimumSize(2000, 600)





    def update_length_width_line_edit(self,length:str,width:str,work_zone:str):
        if work_zone == 'left':
            self.part_length_lin.setText(length)
            self.part_width.setText(width)
            self.workspace_length_lin.setText("")
            self.workspace_width.setText("")
        elif work_zone == 'right':
            self.workspace_length_lin.setText(length)
            self.workspace_width.setText(width)
            self.part_length_lin.setText("")
            self.part_width.setText("")



    def move_workspace_to(self,work_zone:str):
        if work_zone == 'left':
            self.current_work_zone = 'left'
            self.move_to_left_work_zone_button.setDisabled(True)
            self.move_to_right_work_zone_button.setEnabled(True)
            self.update_length_width_line_edit(self.workspace_length_lin.text(),self.workspace_width.text(),work_zone)
        elif work_zone == 'right':
            self.current_work_zone = 'right'
            self.move_to_right_work_zone_button.setDisabled(True)
            self.move_to_left_work_zone_button.setEnabled(True)
            self.update_length_width_line_edit(self.part_length_lin.text(), self.part_width.text(), work_zone)




class SandingCameraPageManager(ModifiedSandingPageView):
    def __init__(self, footer_btn="Camera", parent= None):
        super(SandingCameraPageManager, self).__init__(parent=parent)
        self.__footer_btn_text = footer_btn
        self.camera_widget.newAreaSelectedSignal.connect(self._handle_image_area_selected)
        self.current_unit = MeasureUnitType.MM_UNIT
        self.__dims_widgets = [self.part_width, self.part_length_lin, self.workspace_width, self.workspace_length_lin]

    def new_image_received(self, cam_index:int, pix_map:QtGui.QPixmap):
        if cam_index == 0:
            rect = self.get_part_rect()
            pix_map = pix_map.scaled(self.camera_widget.size())
            if rect is not None:
                self.camera_widget.draw_rectangles(pix_map, rect, QtCore.Qt.darkGreen)
            self.camera_widget.set_image(pix_map)


    def get_part_rect(self):
        part_width, part_length, workspace_width, workspace_length = self.__get_measured_values()
        if part_width > 0 and part_length and workspace_width > 0 and workspace_length > 0:
            part_width_pixels = int((part_width/workspace_width)*self.camera_widget.height())
            part_length_pixels = int((part_length/workspace_length)*self.camera_widget.width())
            generated_rect = QtCore.QRect(0, self.camera_widget.height() - part_width_pixels,
                                 part_length_pixels, part_width_pixels)
            return generated_rect

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

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text


    def is_dirty(self) -> bool:
        return False


    def handle_joint_dowel_profile_updated(self, new_profiles):
        pass

    def handle_setting_changed(self):
        pass

    def change_measure_mode(self, unit: MeasureUnitType):
        self.current_unit = unit
        values = self.__get_measured_values()
        if unit == MeasureUnitType.MM_UNIT:
            factor = 25.4
        else:
            factor = 1/25.4
        for index, widget in enumerate(self.__dims_widgets):
            value = values[index] * factor
            value = round(value, 2)
            widget.setText(str(value))

    def get_part_dimensions(self):
        """this will return the dim in mm """
        values = self.__get_measured_values()
        if self.current_unit == MeasureUnitType.IN_UNIT:
            values = [val*25.4 for val in values]
        return values

    def __get_measured_values(self):
        measures = []
        for widget in self.__dims_widgets:
            text = widget.text()
            if len(text) > 0:
                try:
                    val = float(text)
                    measures.append(val)
                except:
                    measures.append(0)
            else:
                measures.append(0)
        return measures



