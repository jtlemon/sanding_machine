from PySide2 import QtWidgets

from configurations.constants_types import WidgetsType
from custom_widgets.spin_box import CustomSpinBox
from views.custom_app_widgets import TrackableCheckBox




class RenderInternalPramsWidget(QtWidgets.QWidget):
    def __init__(self, widgets_meta_list):  # this just list of prams to create the payload
        super(RenderInternalPramsWidget, self).__init__()
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.internal_widgets = list()
        for index, joint_config in enumerate(widgets_meta_list):
            # these three prams are essential
            lbl_text = joint_config.get("lbl")
            target_key = joint_config.get("target_key")
            widget_type = joint_config.get("field_type", WidgetsType.rangeWidget)
            lbl = QtWidgets.QLabel(lbl_text)
            lbl.setWordWrap(True)
            self.grid_layout.addWidget(lbl, index, 0, 1, 1)
            if widget_type == WidgetsType.rangeWidget:
                widget_range = joint_config.get("range")
                initial_value = widget_range[0]
                if initial_value is None:
                    initial_value = widget_range[0]
                control_widget = CustomSpinBox(
                    *widget_range,
                    initial_mm=initial_value,
                    disp_precession=2,
                    numpad_title=lbl_text,
                    target_config_key=target_key
                )
            else:
                control_widget = TrackableCheckBox(key_name=target_key)
            self.grid_layout.addWidget(control_widget, index, 1, 1, 1)
            self.internal_widgets.append(control_widget)

    def load_initial_values(self, payload: dict):
        for control_widget in self.internal_widgets:
            key = control_widget.get_key()
            if key in payload:
                value = payload.get(key)
                if isinstance(control_widget, CustomSpinBox):
                    control_widget.set_value_and_reset_state(value)
                else:
                    control_widget.set_value(value)

    def get_widget_payload(self):
        payload = {}
        for control_widget in self.internal_widgets:
            key = control_widget.get_key()
            value = control_widget.value()
            payload[key]= value

        return payload


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    from configurations.static_app_configurations import DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION
    w = RenderInternalPramsWidget(DOVETAIL_DOWEL_JOINT_PROFILE_CONFIGURATION)
    w.show()
    app.exec_()
