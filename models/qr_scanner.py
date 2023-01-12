from PySide2 import QtCore


def get_order_number_from_name(order_name: str):
    order_system_number = -1
    order_name = order_name.lstrip("#")
    content = order_name.split(" ")
    if len(content) > 0:
        order_number_str = content[0]
        if order_number_str.isdigit():
            order_system_number = int(order_number_str)
    return order_system_number

class OrderQRScannerManager(QtCore.QObject):
    qrValueChangedSignal = QtCore.Signal(str)
    orderInfoDetectedSignal = QtCore.Signal(int, int) # tld part id , order oms id
    scanningErrSignal = QtCore.Signal()
    detected_string = ""

    def on_new_char_received(self, key_value):
        print(key_value ==  QtCore.Qt.Key_Space)
        if key_value >= QtCore.Qt.Key_Space and key_value <= QtCore.Qt.Key_AsciiTilde:
            self.detected_string += chr(key_value)
            self.qrValueChangedSignal.emit(self.detected_string)
        if key_value == QtCore.Qt.Key_Enter or key_value == QtCore.Qt.Key_Return:
            if len(self.detected_string) == 0:
                return
            tld_part_id = -1
            order_oms_id = -1
            string_parts = self.detected_string.split(",")
            print(string_parts, "split result................")
            if len(string_parts) == 2:
                if string_parts[0].isdigit():
                    tld_part_id = int(string_parts[0])
                order_oms_id = get_order_number_from_name(string_parts[1])
            print(tld_part_id, order_oms_id)
            if tld_part_id > -1 and order_oms_id > -1:
                self.orderInfoDetectedSignal.emit(tld_part_id, order_oms_id)
            else:
                self.scanningErrSignal.emit()
            self.detected_string = "" # to start new scan
