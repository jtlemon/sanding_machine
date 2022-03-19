import serial
from multiprocessing import Process, Queue, Event
import logging
import time
import os
import math
from configurations import common_configurations
module_logger = logging.getLogger("drill-dowel-grbl")
module_logger.setLevel(logging.DEBUG)
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","logs", 'serial_logs.log')
fh = logging.FileHandler(LOG_FILE_PATH)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
module_logger.addHandler(fh)
BAUD_RATE = 115200


class SerialConnector(Process):
    def __init__(self, tx_queue: Queue, tx_direct_queue: Queue, event_queue: Queue,
                 last_responses_queue: Queue, serial_port=None):
        super(SerialConnector, self).__init__()
        self.__prob_commands_tx = Queue(20)
        self.__prob_commands_rx = Queue(20)
        self.__tx_queue = tx_queue
        self.__tx_direct_queue = tx_direct_queue
        self.__event_queue = event_queue
        self.__last_responses_queue = last_responses_queue
        self.__is_serial_connected = False
        self.__serial_dev = None
        self.__serial_port_path = common_configurations.GRBL_MODULE_COM_PORT
        self.__is_simulation_enabled = not common_configurations.IS_GRBL_MODULE_ENABLED
        self.__close_event = Event()
        self.__logging_header = "Simulation" if self.__is_simulation_enabled else "Active"
        self.axis_current_pos_info = {"x": 0, "y": 0, "z": 0, "a": 0}


    def send_message(self, msg_to_send):
        module_logger.debug("({})>> {}".format(self.__logging_header, str(msg_to_send, "utf-8")))
        #print(f'sent {str(msg_to_send, "utf-8")}')
        if self.__is_serial_connected:
            try:
                msg_to_send_str =  msg_to_send.decode()
                if  msg_to_send_str.startswith("hello"):
                    parts = msg_to_send_str.replace("hello", "").split("\r\n")
                    print(parts)
                    for part in parts:
                        if len(part) > 3:
                            msg = part + "\n"
                            self.__serial_dev.write(msg.encode())
                    return

                sent_bytes = self.__serial_dev.write(msg_to_send)
                print(f"{sent_bytes}    sent....")
            except OSError:
                self.__is_serial_connected = False

    def reset_prob_buffer(self):
        while not self.__prob_commands_tx.empty():
            self.__prob_commands_tx.get()
        while not self.__prob_commands_rx.empty():
            self.__prob_commands_rx.get()

    def send_command_directly(self, cmd: bytes, wait_for=500):
        self.__prob_commands_tx.put_nowait((cmd, wait_for))

    def receive_bytes(self, timeout=None):
        rec = []
        try:
            rec = self.__prob_commands_rx.get(block=True, timeout=timeout)
        except:
            pass
        return rec

    def run(self):
        while not self.__close_event.is_set():
            time.sleep(0.05)
            if not self.__is_simulation_enabled and not self.__is_serial_connected:
                self.__reconnect()
                if not self.__is_serial_connected:
                    time.sleep(1)
                    continue
            while not self.__tx_direct_queue.empty():
                cmd_to_send = self.__tx_direct_queue.get()
                self.send_message(cmd_to_send.get("cmd"))
                self.wait_for_response(cmd_to_send)
                if cmd_to_send.get("clr_buffers"):
                    while not self.__tx_direct_queue.empty():
                        self.__tx_direct_queue.get()
                    while not self.__tx_queue.empty():
                        self.__tx_queue.get()
            while not self.__prob_commands_tx.empty():
                cmd_to_send, wait_for = self.__prob_commands_tx.get()
                print("cmd >>>>>>>>>")
                self.__serial_dev.write(cmd_to_send)
                time.sleep(wait_for/1000.0)
                rec_bytes_list = self.__serial_dev.readlines()
                print("<<<<<<<", rec_bytes_list)
                self.__prob_commands_rx.put_nowait(rec_bytes_list)
            if not self.__tx_queue.empty():
                cmd_to_send = self.__tx_queue.get()
                self.send_message(cmd_to_send.get("cmd"))
                self.wait_for_response(cmd_to_send)
            else:
                self.serial_read()
                time.sleep(0.05)

        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except:
                pass
        print("serial process ended suc.........")

    def modify_pos_track_value(self, letter_values:dict):
        axix_displacement = {"x": 0, "y": 0, "z": 0, "a": 0}
        for track_letter, val_str in letter_values.items():
            if len(val_str) and len(track_letter):
                axis_pos = float(val_str)
                displacement = math.fabs(self.axis_current_pos_info[track_letter] - axis_pos)
                self.axis_current_pos_info[track_letter] = axis_pos
                axix_displacement[track_letter] = displacement
        self.__event_queue.put({"type": "displacement", "value": axix_displacement})

    def wait_for_response(self, cmd_to_send):
        start_time = time.time()
        response = ""
        while len(response) < 2 and (time.time() - start_time) < 5 and not self.fast_interrupt_occur():
            response = self.serial_read(True)
        #########################################################
        cmd = str(cmd_to_send.get("cmd") , "utf-8")
        if len(response) > 0:
            self.__last_responses_queue.put({"cmd":cmd, "response":response})
            if "error" not in response:
                if cmd.startswith("m74"):
                    self.__event_queue.put({"type": "dowel_inserted"})
                elif cmd.startswith("g1"):
                    self.__event_queue.put({"type": "hole_drilled"})
                elif cmd.startswith("g0"):
                    cmd = cmd.replace("g0" , "")
                    #x-150y-15z-10a-3
                    val_str = ""
                    track_letter = ""
                    letters_values = dict()
                    for letter in cmd:
                        if letter in ["x", "y", "z", "a"]:
                            letters_values[track_letter] = val_str
                            track_letter = letter
                            val_str = ""
                        elif letter.isdigit():
                            val_str += letter
                    letters_values[track_letter] = val_str
                    self.modify_pos_track_value(letters_values)
        notify_message = cmd_to_send.get("notify_message")
        if len(notify_message) > 0:
            if notify_message != "emit_measure_response":
                self.__event_queue.put({"type": "notification", "value": notify_message})
            else:
                self.__event_queue.put({"type": "received_response", "value": notify_message, "response":response})
        if cmd_to_send.get("wait_time") > 0:
            start_time = time.time()
            while time.time() - start_time < cmd_to_send.get("wait_time") and not self.fast_interrupt_occur():
                time.sleep(0.01)
        return response

    def fast_interrupt_occur(self):
        return not self.__tx_direct_queue.empty()

    def serial_read(self, after_cmd=False):
        rec = ""
        if not self.__is_simulation_enabled:
            if self.__is_serial_connected:
                try:
                    while self.__serial_dev.inWaiting() > 0:
                        tmp = self.__serial_dev.read_until()
                        rec += str(tmp, "utf-8")
                        if len(rec) > 1:
                            if after_cmd is False:
                                # update the buffer in dummy read case only
                                self.__last_responses_queue.put({"cmd": "", "response": rec})
                            module_logger.debug(f"({self.__logging_header})<< {rec}")
                except OSError:
                    self.__is_serial_connected = False
                    self.__event_queue.put({"type":"notification", "value":"usb not connected"})
                    return "error"
                except  Exception as e:
                    print(e)
            else:
                return "error"
        else:
            if after_cmd:
                rec = "ok"
                module_logger.debug(f"({self.__logging_header})<< {rec}")
        return rec

    def __reconnect(self):
        self.__is_serial_connected = False
        # try to close the port
        if self.__serial_dev:
            try:
                self.__serial_dev.close()
            except (serial.SerialException, OSError):
                self.__serial_dev = None
        try:
            self.__serial_dev = serial.Serial(self.__serial_port_path, BAUD_RATE, timeout=0.5)
            if self.__serial_dev.isOpen():
                self.__is_serial_connected = True
                self.__event_queue.put({"type": "notification", "value": "connected"})
                self.__serial_dev.flush()
        except (serial.SerialException, OSError):
            pass

    def get_connection_status(self):
        return "connected" if self.__is_serial_connected else "usb not connected"

    def add_new_command(self, cmd: str, cmd_type: str = 'g', wait_after: int = 0, notify_message: str = ""):
        if cmd_type == "g":
            cmd = cmd + "\r\n"
        command_bytes = bytes(cmd, "utf-8")
        command_to_send = {"cmd": command_bytes, "wait_time": wait_after, "notify_message": notify_message}
        self.__tx_queue.put(command_to_send)

    def send_direct_command(self, cmd: str, cmd_type: str = 'g', notify_message: str = "", clr_buffer=False):
        if cmd_type == "g":
            cmd = cmd + "\n"
        command_bytes = bytes(cmd, "utf-8")
        command_to_send = {"cmd": command_bytes, "wait_time": 0, "notify_message": notify_message,
                           "clr_buffers": clr_buffer}
        self.__tx_direct_queue.put(command_to_send)

    def close_service(self):
        self.__close_event.set()

