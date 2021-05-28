from PySide2 import QtWidgets,QtCore, QtGui


def add_item_to_table(table, row, col, value, color=None):
    item = QtWidgets.QTableWidgetItem(str(value))
    item.setTextAlignment(QtCore.Qt.AlignCenter)
    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
    if color:
        item.setForeground(QtGui.QBrush(color))
    item.setToolTip(f"<b>{str(value)}</b>")
    table.setItem(row, col, item)


def display_error_message(message, title="Error", parent= None):
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()

def display_question_dialog(question, title, parent):
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(question)
    msg.addButton(QtWidgets.QMessageBox.Yes)
    msg.addButton(QtWidgets.QMessageBox.No)
    return msg.exec_()

def display_information_dialog(message, title, parent):
    msg = QtWidgets.QMessageBox(parent)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()
