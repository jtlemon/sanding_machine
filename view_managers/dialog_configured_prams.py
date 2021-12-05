from PySide2 import QtWidgets

from configurations.constants_types import WidgetsType
from custom_widgets.spin_box import CustomSpinBox
from views.custom_app_widgets import TrackableCheckBox, TrackableLineEdit, TrackableQComboBox

class OptionalRangeWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionalRangeWidget, self).__init__()
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.spinbox = CustomSpinBox(*args, **kwargs)
        self.widget_layout.addWidget(self.spinbox, stretch=1)
        self.widget_layout.addWidget(QtWidgets.QLabel("Active"))
        self.check_box = QtWidgets.QCheckBox()
        self.widget_layout.addWidget(self.check_box)
        self.check_box.toggled.connect(lambda state:self.spinbox.setEnabled(state))

    def value(self):
        if self.check_box.isChecked():
            return self.spinbox.value()
        else:
            return None

    def set_value_and_reset_state(self, value):
        if value is None:
            self.spinbox.set_value_and_reset_state(0)
            self.check_box.setChecked(False)
            self.spinbox.setEnabled(False)
        else:
            self.spinbox.set_value_and_reset_state(value)
            self.check_box.setChecked(True)
            self.spinbox.setEnabled(True)

    def get_key(self):
        return self.spinbox.get_key()




def widget_create_from_dict(config_dict):
    name = config_dict.get("lbl")
    key = config_dict.get("target_key")
    field_type = config_dict.get("field_type", WidgetsType.rangeWidget)
    control_widget = None
    if field_type == WidgetsType.rangeWidget or field_type==WidgetsType.optionalRangeWidget:
        widget_range = config_dict.get("range")
        initial_value = widget_range[0]
        if initial_value is None:
            initial_value = widget_range[0]
        unit = config_dict.get("unit", "")
        disp_precession = config_dict.get("precession", 2)
        allow_mode_change = True if len(unit) == 0 else False
        if field_type==WidgetsType.optionalRangeWidget:
            target_widget_class =  OptionalRangeWidget
        else:
            target_widget_class = CustomSpinBox
        control_widget = target_widget_class(
            *widget_range,
            initial_mm=initial_value,
            disp_precession=disp_precession,
            numpad_title=name,
            target_config_key=key,
            allow_mode_change=allow_mode_change,
            extra=unit

        )
    elif field_type == WidgetsType.boolWidget:
        control_widget = TrackableCheckBox(key_name=key)
    elif field_type == WidgetsType.textWidget:
        control_widget = TrackableLineEdit(key_name=key)
    elif field_type == WidgetsType.speedWidget:
        widget_range = config_dict.get("range")
        initial_value = widget_range[0]
        unit = config_dict.get("unit", "")
        allow_mode_change = True if len(unit) == 0 else False
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
            special_lbl=custom_lbl,
            allow_mode_change=allow_mode_change
        )
    elif field_type == WidgetsType.optionWidget:
        options = config_dict.get("options")
        control_widget = TrackableQComboBox(key_name=key, options=options)

    return name, key, control_widget


def set_field_value(control_widget, value):
    if isinstance(control_widget, CustomSpinBox) or isinstance(control_widget, OptionalRangeWidget):
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

    def get_internal_widgets_ref(self):
        return  self.internal_widgets

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
