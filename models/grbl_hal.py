import datetime
import logging
import os
from multiprocessing import Queue

from PySide2 import QtCore

from apps.maintenance_productivity.models import Dowels, Holes, Part, AxisMotion
from configurations import MainConfigurationLoader
from models.generateCode import GenerateCode
from .grbl_serial_connector import SerialConnector
import configurations.static_app_configurations as static_configurations

module_logger = logging.getLogger(static_configurations.LOGGER_NAME)


class GrblControllerHal(QtCore.QObject):
    servoStartSignal = QtCore.Signal(bool)
    machineStartedSignal = QtCore.Signal(int)
    machineStateChangedSignal = QtCore.Signal(str)

    def __init__(self, serial_port=None):
        super(GrblControllerHal, self).__init__()
        self.__current_dowel_profile = None
        self.__current_bit_profile = None
        self.__current_joint_profile = None

        self.__tx_queue = Queue(1000)
        self.__tx_direct_queue = Queue(20)
        self.__event_queue = Queue(50)
        self.__last_responses_queue = Queue(50)
        self.__event_timer = QtCore.QTimer()
        self.__event_timer.timeout.connect(self.check_events)
        self.__event_timer.start(100)
        self.grbl_stream = SerialConnector(self.__tx_queue, self.__tx_direct_queue, self.__event_queue,
                                           self.__last_responses_queue, serial_port)
        self.grbl_stream.daemon = True
        # self.grbl_stream.status.connect(self.dev_status_change)
        self.spindle_state = False
        self.__current_state = ""
        # noinspection PyUnusedLocal
        self.sensor_readings = [0 for i in range(10)]  # hold the latest sensor readings
        # create timer to reset machine after 2 sec
        self.startup_timer = QtCore.QTimer()
        self.startup_timer.setSingleShot(True)
        self.startup_timer.timeout.connect(lambda: self.reset_and_home())
        self.startup_timer.start(2000)

        self.__rest_timer = QtCore.QTimer()
        self.__rest_timer.setSingleShot(True)
        self.__rest_timer.timeout.connect(lambda: self.turn_on_machine_after_reset())
        self.auto_right_width = 0
        self.auto_left_width = 0

        self.__spindle_timer = QtCore.QTimer()
        self.__spindle_timer.setSingleShot(True)
        self.__spindle_timer.timeout.connect(lambda: self.spindle_off())

    def start_process(self):
        self.grbl_stream.start()

    def handle_auto_left_right_width_changed(self, left_width: float, right_width: float):
        # @Todo make sure that this values are fixed during the machine operation
        self.auto_left_width = left_width
        self.auto_right_width = right_width

    def get_latest_responses(self):
        all_responses = []
        while not self.__last_responses_queue.empty():
            response = self.__last_responses_queue.get()
            all_responses.append(response)
        return all_responses

    def handle_physical_error_signal(self, signal):
        """ this signal captured from arduino"""
        self.turn_off_machine()

    def dev_status_change(self, new_state):
        self.machineStateChangedSignal.emit(new_state)

    def cycle_start_left(self, mode, current_profile=[]):
        if mode == "manual":
            left_width = MainConfigurationLoader.get_left_active_value() * 25.4
        else:
            left_width = self.auto_left_width
        Part(part_size=left_width, mode=mode, direction="left").save()
        self.__current_state = 'pending'
        self.emit_new_state()
        generate = GenerateCode()  # need to pass left and right widths here
        self.spindle_on()
        with open('.test_g_code.nc', 'w') as f:
            f.write('\n'.join(map(str, generate.calculate(left_width, 0, current_profile))))

        with open('.test_g_code.nc', 'r') as g:
            for line in g:
                self.grbl_stream.add_new_command(line.strip())
        os.remove('.test_g_code.nc')
        self.__current_state = 'ready'
        self.emit_new_state()
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)
        del generate

    def cycle_start_right(self, mode, current_profile=[]):
        if mode == 'manual':
            right_width = MainConfigurationLoader.get_right_active_value() * 25.4
        else:
            right_width = self.auto_right_width
        Part(part_size=right_width, mode=mode, direction="right").save()
        self.__current_state = 'pending'
        self.emit_new_state()
        generate = GenerateCode()
        self.spindle_on()
        with open('.test_g_code.nc', 'w') as f:
            f.write('\n'.join(map(str, generate.calculate(0, right_width, current_profile))))

        with open('.test_g_code.nc', 'r') as g:
            for line in g:
                self.grbl_stream.add_new_command(line.strip())
        os.remove('.test_g_code.nc')

        self.__current_state = 'ready'
        self.emit_new_state()
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)
        del generate

    def reference_back(self, width, side, current_profile=[]):
        module_logger.debug(f"reference back {side} with width={width}")
        # this will instantiate generate code and call back_reference() function to generate the g-code,
        # and run a cycle similar to cycle_start() but with the g-code generated by this
        self.__current_state = 'pending'
        self.emit_new_state()
        generate = GenerateCode()  # need to pass left and right widths here
        self.spindle_on()
        with open('.back_g_code.nc', 'w') as f:
            f.write('\n'.join(map(str, generate.back_reference(width, side, current_profile))))

        with open('.back_g_code.nc', 'r') as g:
            for line in g:
                self.grbl_stream.add_new_command(line.strip())
        # os.remove('.back_g_code.nc')
        self.__current_state = 'ready'
        self.emit_new_state()
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)
        del generate

    def custom_size(self, width, side, current_profile=[]):
        self.__current_state = 'pending'
        self.emit_new_state()
        generate = GenerateCode()
        self.spindle_on()
        with open('.custom_g_code.nc', 'w') as f:
            f.write('\n'.join(map(str, generate.custom_size(width, side, current_profile))))

        with open('.custom_g_code.nc', 'r') as g:
            for line in g:
                self.grbl_stream.add_new_command(line.strip())
        # os.remove('.custom_g_code.nc')
        self.__current_state = 'ready'
        self.emit_new_state()
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)
        del generate

    def purge(self):
        self.grbl_stream.add_new_command('g0x0y0z0')
        self.grbl_stream.add_new_command('g0a-50')
        self.grbl_stream.add_new_command('m78')
        self.grbl_stream.add_new_command('g4p.5')
        self.grbl_stream.add_new_command('m79')
        self.grbl_stream.add_new_command('g4p.5')
        self.grbl_stream.add_new_command('m78')
        self.grbl_stream.add_new_command('g4p.5')
        self.grbl_stream.add_new_command('m79')
        self.grbl_stream.add_new_command('g4p.5')
        module_logger.debug("machine purgeing")

    def clear_dowel(self):
        self.park()
        self.grbl_stream.add_new_command('m74')
        self.grbl_stream.add_new_command('g4p.5')
        self.grbl_stream.add_new_command('m75')
        module_logger.debug("machine clearing")

    def park(self):
        self.spindle_off()
        self.deactivate_solenoids()
        self.grbl_stream.add_new_command('g0x-520y-15z0a0')
        module_logger.debug("parking machine")

    def spindle_on(self):
        spindle_time_out = MainConfigurationLoader.get_spindle_off_value()
        spindle_speed = MainConfigurationLoader.get_spindle_speed_value()
        if self.spindle_state:
            self.__spindle_timer.start(spindle_time_out * 1000)
            self.grbl_stream.add_new_command(f'm3s{spindle_speed}')
            module_logger.debug("spindle is already on")
        else:
            self.spindle_state = True
            self.grbl_stream.add_new_command(f'm3s{spindle_speed}')
            self.grbl_stream.add_new_command('g4p3')
            self.__spindle_timer.start(spindle_time_out * 1000)
            module_logger.debug("turning spindle on")

    def spindle_off(self):
        self.spindle_state = False
        self.grbl_stream.add_new_command('m5')
        module_logger.debug("turning spindle off")

    def deactivate_solenoids(self):
        self.grbl_stream.add_new_command('m63')
        self.grbl_stream.add_new_command('m65')
        self.grbl_stream.add_new_command('m67')
        self.grbl_stream.add_new_command('m69')
        self.grbl_stream.add_new_command('m71')
        self.grbl_stream.add_new_command('m73')
        self.grbl_stream.add_new_command('m75')
        self.grbl_stream.add_new_command('m77')
        self.grbl_stream.add_new_command('m79')
        self.grbl_stream.add_new_command('m81')

    def emit_new_state(self):
        self.machineStateChangedSignal.emit(self.__current_state)

    def calculate_run_time(self):
        # this machine will requre a different strategy to calculate run time.  will need a base time + time per each dowel
        return 10

    def cancel(self):
        self.spindle_off()
        self.deactivate_solenoids()
        self.grbl_stream.send_direct_command("i", clr_buffer=True)

    def reset_machine(self):
        module_logger.debug("reset the machine")
        self.grbl_stream.send_direct_command(chr(0x85), clr_buffer=True)
        self.turn_off_machine()
        self.__rest_timer.start(2000)

    def turn_on_machine_after_reset(self):
        self.turn_on_machine()
        self.grbl_stream.add_new_command("$H")
        self.grbl_stream.add_new_command("g10 p0 l20 x0 y0 z0", notify_message='Homing Complete-Ready')

    def turn_on_machine(self):
        module_logger.debug("turn on the machine")
        self.servoStartSignal.emit(True)

    def turn_off_machine(self):
        module_logger.debug("turn off the machine")
        self.servoStartSignal.emit(False)

    def move_to_home(self):
        self.deactivate_solenoids()
        self.spindle_off()
        self.grbl_stream.send_direct_command("$H", clr_buffer=True)
        self.grbl_stream.add_new_command("g10 p0 l20 x0 y0 z0", notify_message='Homing Complete-Ready')

    def reset_and_home(self):
        self.grbl_stream.add_new_command('$slp')
        self.grbl_stream.add_new_command(chr(0x18), wait_after=2, notify_message="Homing")
        self.grbl_stream.add_new_command(chr(0x18), wait_after=2, notify_message="Homing")
        self.grbl_stream.add_new_command("")
        self.grbl_stream.add_new_command("$H")
        self.grbl_stream.add_new_command("g10 p0 l20 x0 y0 z0 a0", notify_message='Homing Complete-Ready')

    def check_events(self):
        total_num_of_holes = 0
        total_num_of_dowels = 0
        axis_value_changed_flag = False
        x_offset, y_offset, z_offset, a_offset = 0, 0, 0, 0
        cur_date = datetime.datetime.now().date()
        while not self.__event_queue.empty():
            event = self.__event_queue.get()
            if event.get("type") == "notification":
                self.machineStateChangedSignal.emit(event.get("value"))
            elif event.get("type") == "displacement":
                displacement_dict = event.get("value")
                for key, val in displacement_dict.items():
                    axis_value_changed_flag = True
                    if key == "x":
                        x_offset += val
                    elif key == "y":
                        y_offset += val
                    elif key == "z":
                        z_offset += val
                    elif key == "a":
                        a_offset += val
            elif event.get("type") == "dowel_inserted":
                total_num_of_dowels += 1
            elif event.get("type") == "hole_drilled":
                total_num_of_holes += 1

        if axis_value_changed_flag is True:
            p, created = AxisMotion.objects.get_or_create(
                date=cur_date
            )
            p.x_axis += x_offset
            p.y_axis += y_offset
            p.z_axis += z_offset
            p.a_axis += a_offset
            p.date = cur_date
            p.save()

        if total_num_of_dowels > 0:
            p, created = Dowels.objects.get_or_create(
                date=cur_date
            )
            p.no_of_dowel += total_num_of_dowels
            p.date = cur_date
            p.save()

        if total_num_of_holes > 0:
            p, created = Holes.objects.get_or_create(
                date=cur_date
            )
            p.no_of_holes += total_num_of_holes
            p.date = cur_date
            p.save()
    # *****************  added from the old code *************************
    def cycle_start_1(self):
        """
        @ToDo added from the old code we have to check it
        """
        self.turn_on_machine()
        self.machineStateChangedSignal.emit("pending- cycle 1")
        self.clamp_right_vertical()
        self.clamp_left_vertical()
        self.retract_locating_bar()

    def cycle_start_2(self):
        self.machineStateChangedSignal.emit("pending- cycle 2")
        self.clamp_right_horizontal()
        self.clamp_left_horizontal()
        # @ToDo generate grbl code
        self.machineStateChangedSignal.emit('ready')
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)

    def release_clamp_left_vertical(self):
        module_logger.debug('releasing left vertical clamp')
        self.grbl_stream.add_new_command('m71')

    def release_clamp_right_vertical(self):
        module_logger.debug('releasing right vertical clamp')
        self.grbl_stream.add_new_command('m73')

    def clamp_left_vertical(self):
        module_logger.debug('clamping left vertical')
        self.grbl_stream.add_new_command('m70')

    def clamp_right_vertical(self):
        module_logger.debug('clamping right vertical')
        self.grbl_stream.add_new_command('m72')

    def retract_locating_bar(self):
        module_logger.debug('retracting locating bar')
        self.grbl_stream.add_new_command('m69')

    def extend_locating_bar(self):
        module_logger.debug('extending locating bar')
        self.grbl_stream.add_new_command('m68')

    def clamp_right_horizontal(self):
        self.grbl_stream.add_new_command('m66')

    def release_clamp_right_horizontal(self):
        self.grbl_stream.add_new_command('m67')

    def clamp_left_horizontal(self):
        self.grbl_stream.add_new_command('m62')


    def update_machine_profiles(self, joint_profile, bit_profile, dowel_profile):
        self.__current_dowel_profile = dowel_profile
        self.__current_bit_profile = bit_profile
        self.__current_joint_profile = joint_profile

    def release_resources(self):
        self.deactivate_solenoids()
        self.spindle_off()
        self.turn_off_machine()
        self.grbl_stream.close_service()

