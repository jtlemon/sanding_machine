from PySide2 import QtWidgets, QtCore, QtGui


class RecordTrackBtn(QtWidgets.QPushButton):
    customClickSignal = QtCore.Signal(int)

    def __init__(self, record_id, icon_path=None):
        super(RecordTrackBtn, self).__init__()
        self.__current_id = record_id
        if icon_path:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(30, 30))
        self.clicked.connect(lambda: self.customClickSignal.emit(record_id))

    def get_id(self):
        return self.__current_id


class AppFooterButton(QtWidgets.QPushButton):
    customClickSignal = QtCore.Signal(int)

    def __init__(self, *args, target_page=-1, **kwargs):
        super(AppFooterButton, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.clicked.connect(lambda: self.customClickSignal.emit(target_page))


class ProfileComboBox(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ProfileComboBox, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_layout.setSpacing(0)
        self.combo_box = QtWidgets.QComboBox()
        self.widget_layout.addWidget(self.combo_box, stretch=1)
        self.action_combo_btn = QtWidgets.QPushButton()
        self.action_combo_btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.action_combo_btn.setObjectName("action_combo_btn")
        self.action_combo_btn.setIconSize(QtCore.QSize(35, 35))
        self.widget_layout.addWidget(self.action_combo_btn, stretch=0)
        self.setMinimumHeight(50)
        self.action_combo_btn.clicked.connect(lambda: self.combo_box.showPopup())
        self.currentTextChanged = self.combo_box.currentTextChanged

    def addItems(self, items):
        self.combo_box.addItems(items)

    def clear(self):
        self.combo_box.clear()

    def currentIndex(self):
        return self.combo_box.currentIndex()

    def currentText(self):
        return self.combo_box.currentText()

    def setCurrentIndex(self, index):
        self.combo_box.setCurrentIndex(index)

    def setCurrentText(self, text):
        self.combo_box.setCurrentText(text)

    def set_default_option(self, default):
        index = self.combo_box.findText(default)
        self.combo_box.setCurrentIndex(index)

    def load_new_options(self, options):
        current_option = self.combo_box.currentText()
        self.combo_box.clear()
        self.combo_box.addItems(options)
        target_index = self.combo_box.findText(current_option)
        self.combo_box.setCurrentIndex(target_index)


class SaveCancelButtons(QtWidgets.QWidget):
    def __init__(self):
        super(SaveCancelButtons, self).__init__()
        # save/cancel buttons
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setMinimumSize(200, 60)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setMinimumSize(200, 60)
        self.footer_layout = QtWidgets.QHBoxLayout(self)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.footer_layout.addItem(h_spacer_item_1)
        self.footer_layout.addWidget(self.cancel_btn)
        self.footer_layout.addWidget(self.save_btn)
        self.footer_layout.addItem(h_spacer_item_2)


class QLineEditWithSideLabel(QtWidgets.QWidget):
    def __init__(self, lbl_txt, line_text=""):
        super(QLineEditWithSideLabel, self).__init__()
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_lbl = QtWidgets.QLabel(lbl_txt)
        self.text_edit_widget = QtWidgets.QLineEdit(line_text)
        self.widget_layout.addWidget(self.widget_lbl, stretch=0)
        self.widget_layout.addWidget(self.text_edit_widget, stretch=1)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_1)

    def setText(self, text):
        self.text_edit_widget.setText(text)

    def text(self):
        return self.text_edit_widget.text()


class CenterPagePushButton(QtWidgets.QWidget):
    def __init__(self, btn_text="", icon_path=None):
        super(CenterPagePushButton, self).__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        h_spacer_item_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_1)
        self.widget_btn = QtWidgets.QPushButton(btn_text)
        self.widget_layout.addWidget(self.widget_btn)
        self.widget_btn.setObjectName("center_btn_widget")
        if icon_path:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.widget_btn.setIcon(icon)
            self.widget_btn.setIconSize(QtCore.QSize(30, 30))
        h_spacer_item_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                QtWidgets.QSizePolicy.Preferred)
        self.widget_layout.addItem(h_spacer_item_2)
        self.clicked = self.widget_btn.clicked


class TrackableCheckBox(QtWidgets.QCheckBox):
    def __init__(self, *args, key_name, **kwargs):
        super(TrackableCheckBox, self).__init__(*args, **kwargs)
        self.__key_name = key_name

    def get_key(self):
        return self.__key_name

    def set_value(self, new_value):
        self.setChecked(True if new_value else False)

    def value(self):
        return self.isChecked()


class TrackableLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, key_name, **kwargs):
        super(TrackableCheckBox, self).__init__(*args, **kwargs)
        self.__key_name = key_name

    def get_key(self):
        return self.__key_name

    def set_value(self, new_value):
        self.setText(new_value)

    def value(self):
        return self.text()


class TrackableQComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, key_name, options=[], **kwargs):
        super(TrackableQComboBox, self).__init__(*args, **kwargs)
        self.__key_name = key_name
        self.addItems(options)

    def get_key(self):
        return self.__key_name

    def set_value(self, new_value):
        self.setCurrentText(new_value)

    def value(self):
        return self.currentText()


class ProfileAddEditWidget(QtWidgets.QWidget):
    def __init__(self, profile_descriptors: list, add_edit_dialog_class, db_model, parent=None,
                 append_bit_profile=False):
        super(ProfileAddEditWidget, self).__init__(parent)
        self.add_edit_dialog_class = add_edit_dialog_class
        self.profile_db_model = db_model
        self.__sanding_door_styles = set()
        self.append_bit_profile_option = append_bit_profile
        self.widget_layout = QtWidgets.QVBoxLayout(self)
        # header
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.addStretch(1)
        self.add_profile_btn = QtWidgets.QPushButton("add new profile")
        self.add_profile_btn.setMinimumSize(300, 60)
        self.header_layout.addWidget(self.add_profile_btn)
        self.header_layout.addStretch(1)
        self.widget_layout.addLayout(self.header_layout)
        # table
        col_names = ["name"]
        self.target_db_keys_defaults = dict()
        for profile_descriptor in profile_descriptors:
            lbl_text = profile_descriptor.get("lbl")
            target_key = profile_descriptor.get("target_key")
            widget_range = profile_descriptor.get("range", None)
            if widget_range is not None:
                self.target_db_keys_defaults[target_key] = widget_range[0]
            else:
                self.target_db_keys_defaults[target_key] = None

            col_names.append(lbl_text)

        if self.append_bit_profile_option:
            col_names.extend(["Bit", "#", "#"])
        else:
            col_names.extend(["#", "#"])
        self.widget_table = QtWidgets.QTableWidget()
        self.widget_table.setColumnCount(len(col_names))
        self.widget_table.setHorizontalHeaderLabels(col_names)
        for i in range(self.widget_table.columnCount() - 2):
            self.widget_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.widget_layout.addWidget(self.widget_table, stretch=1)
        self.add_profile_btn.clicked.connect(self.handle_add_profile)
        self.handle_reload_profiles()

    def handle_reload_profiles(self):
        for profile in self.profile_db_model.objects.all():
            self.append_profile_to_table(profile, is_new=True)
            self.__sanding_door_styles.add(profile.profile_name)

    def append_profile_to_table(self, target_profile, is_new=False):
        has_to_update_model = False
        if is_new is True:
            row_index = self.widget_table.rowCount()
            self.widget_table.insertRow(row_index)
        else:
            row_index = self.get_row_id(target_profile.pk)
        self.add_item_to_table(row_index, 0, target_profile.profile_name)
        for col_index, key in enumerate(self.target_db_keys_defaults):
            default_value = self.target_db_keys_defaults.get(key)
            value = target_profile.get_value(key)
            if (value is None) and (default_value is not None):
                has_to_update_model = True
                value = default_value
                target_profile.set_value(key, value)
            self.add_item_to_table(row_index, col_index + 1, value)
        col_index = col_index + 2
        if self.append_bit_profile_option is True:
            self.add_item_to_table(row_index, col_index, target_profile.bit_profile.profile_name)
            col_index += 1
        if is_new is True:
            edit_btn = RecordTrackBtn(target_profile.pk, ":/icons/icons/icons8-edit-96.png")
            del_btn = RecordTrackBtn(target_profile.pk, ":/icons/icons/icons8-delete-bin-96.png")
            self.widget_table.setCellWidget(row_index, col_index, edit_btn)
            self.widget_table.setCellWidget(row_index, col_index + 1, del_btn)
            edit_btn.customClickSignal.connect(self.handle_edit_profile)
            del_btn.customClickSignal.connect(self.handle_delete_profile)
            if has_to_update_model:
                target_profile.save()

    def add_item_to_table(self, row, col, value):
        item = QtWidgets.QTableWidgetItem(str(value))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        item.setToolTip(f"<b>{str(value)}</b>")
        self.widget_table.setItem(row, col, item)

    def del_profile_by_object_id(self, object_id):
        row_id = self.get_row_id(object_id)
        self.widget_table.removeRow(row_id)

    def get_row_id(self, item_pk):
        row_id = -1
        for row_index in range(self.widget_table.rowCount()):
            lst_btn = self.widget_table.cellWidget(row_index, self.widget_table.columnCount() - 1)
            if item_pk == lst_btn.get_id():
                row_id = row_index
        if row_id < 0:
            raise ValueError(f"the id field should be > 0 order pk {item_pk}")
        return row_id

    def handle_add_profile(self):
        dia = self.add_edit_dialog_class(parent=self)
        if dia.exec_():
            new_profile = dia.get_profile()
            self.append_profile_to_table(new_profile, is_new=True)
            self.__sanding_door_styles.add(new_profile.profile_name)
            self.profileChanged.emit(self.__sanding_door_styles)

    def handle_edit_profile(self, profile_id: int):
        target_profile = self.profile_db_model.objects.get(pk=profile_id)
        old_profile_name = target_profile.profile_name
        dia = self.add_edit_dialog_class(door_style_profile=target_profile, parent=self)
        if dia.exec_():
            new_profile = dia.get_profile()
            self.append_profile_to_table(new_profile, is_new=False)
            if old_profile_name != new_profile.profile_name:
                self.__sanding_door_styles.remove(old_profile_name)
                self.__sanding_door_styles.add(new_profile.profile_name)
                self.profileChanged.emit(self.__sanding_door_styles)

    def handle_delete_profile(self, profile_id: int):
        profile = self.profile_db_model.objects.get(pk=profile_id)
        self.__sanding_door_styles.remove(profile.profile_name)
        profile.delete()
        self.del_profile_by_object_id(profile_id)
        self.profileChanged.emit(self.__sanding_door_styles)

    def get_loaded_profiles(self):
        return self.__sanding_door_styles
