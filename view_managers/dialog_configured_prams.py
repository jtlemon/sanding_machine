from PySide2 import QtWidgets

from configurations.constants_types import WidgetsType
from custom_widgets.spin_box import CustomSpinBox
from views.custom_app_widgets import TrackableCheckBox, TrackableLineEdit, TrackableQComboBox


def widget_create_from_dict(config_dict):
    name = config_dict.get("lbl")
    key = config_dict.get("target_key")
    field_type = config_dict.get("field_type", WidgetsType.rangeWidget)
    control_widget = None
    if field_type == WidgetsType.rangeWidget:
        widget_range = config_dict.get("range")
        initial_value = widget_range[0]
        if initial_value is None:
            initial_value = widget_range[0]
        control_widget = CustomSpinBox(
            *widget_range,
            initial_mm=initial_value,
            disp_precession=2,
            numpad_title=name,
            target_config_key=key
        )
    elif field_type == WidgetsType.boolWidget:
        control_widget = TrackableCheckBox(key_name=key)
    elif field_type == WidgetsType.textWidget:
        control_widget = TrackableLineEdit(key_name=key)
    elif field_type == WidgetsType.speedWidget:
        widget_range = config_dict.get("range")
        initial_value = widget_range[0]
        unit = config_dict.get("unit", "")
        custom_lbl = config_dict.get("custom_lbl", {})
        if initial_value is None:
            initial_value = widget_range[0]
        control_widget = CustomSpinBox(
            *widget_range,
            initial_mm=initial_value,
            disp_precession=0,
            extra=unit,
            target_config_key=key,
            numpad_title=name,
            special_lbl=custom_lbl
        )
    elif field_type == WidgetsType.optionWidget:
        options = config_dict.get("options")
        control_widget = TrackableQComboBox(key_name=key, options=options)

    return name, key, control_widget


def set_field_value(control_widget, value):
    if isinstance(control_widget, CustomSpinBox):
        control_widget.set_value_and_reset_state(value)
    else:
        control_widget.set_value(value)


class RenderInternalPramsWidget(QtWidgets.QWidget):
    def __init__(self, widgets_meta_list):  # this just list of prams to create the payload
        super(RenderInternalPramsWidget, self).__init__()
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.internal_widgets = list()
        for index, joint_config in enumerate(widgets_meta_list):
            # these three prams are essential
            name, key, control_widget = widget_create_from_dict(joint_config)
            lbl = QtWidgets.QLabel(name)
            lbl.setWordWrap(True)
            self.grid_layout.addWidget(lbl, index, 0, 1, 1)
            self.grid_layout.addWidget(control_widget, index, 1, 1, 1)
            self.internal_widgets.append(control_widget)

    def load_initial_values(self, payload: dict):
        for control_widget in self.internal_widgets:
            key = control_widget.get_key()
            if key in payload:
                value = payload.get(key)
                set_field_value(control_widget, value)

    def get_widget_payload(self):
        payload = {}
        for control_widget in self.internal_widgets:
            key = control_widget.get_key()
            value = control_widget.value()
            payload[key] = value
        return payload


if __name__ == "__main__":
    from views import utils

    app = QtWidgets.QApplication([])
    from configurations.static_app_configurations import DOVETAIL_BIT_PROFILES_CONFIGURATION

    w = RenderInternalPramsWidget(DOVETAIL_BIT_PROFILES_CONFIGURATION)
    w.show()
    app.setStyleSheet(utils.load_app_style())
    app.exec_()
