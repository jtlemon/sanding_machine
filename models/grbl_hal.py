import datetime
import logging
import os
from multiprocessing import Queue

from PySide2 import QtCore

from apps.maintenance_productivity.models import Dowels, Holes, Part, AxisMotion
from configurations import MainConfigurationLoader
from models.generateCode import GenerateCode
from .grbl_serial_connector import SerialConnector
from configurations import common_configurations
from configurations.custom_pram_loader import CustomMachineParamManager
import time
from models import db_utils

module_logger = logging.getLogger(common_configurations.LOGGER_NAME)


class GrblControllerHal(QtCore.QObject):
    servoStartSignal = QtCore.Signal(bool)
    machineStartedSignal = QtCore.Signal(int)
    machineStateChangedSignal = QtCore.Signal(str)
    newBitLengthCaptured = QtCore.Signal(float)
    bitNotLoadedSignal = QtCore.Signal()

    def __init__(self, serial_port=None):
        super(GrblControllerHal, self).__init__()
        self.__measure_prob_counter = 0
        self.__retrieved_z_values = list()
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
        self.grbl_stream.add_new_command('g90', notify_message='Parking')
        self.grbl_stream.add_new_command('g0z0')
        self.grbl_stream.add_new_command('g0x-150y0', notify_message='Parked-Ready')
        module_logger.debug("parking machine")

    def spindle_on(self):
        spindle_time_out = CustomMachineParamManager.get_value("spindle_time_out")
        # spindle_speed = CustomMachineParamManager.get_value("spindle_speed")
        spindle_speed = CustomMachineParamManager.get_value("probe_spindle_speed")
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

    def set_fences(self):
        from models.dovetail_code_generator_new import GenerateCode
        grbl_generator = GenerateCode()
        grbl_generator.set_fences()
        g_code = grbl_generator.g_code
        for cmd in g_code:
            print(f"debug_fence{cmd}")
            self.grbl_stream.add_new_command(cmd)

    def emit_new_state(self):
        self.machineStateChangedSignal.emit(self.__current_state)

    def calculate_run_time(self):
        # this machine will requre a different strategy to calculate run time.  will need a base time + time per each dowel
        return 10

    def cancel(self):
        """
        this cancel behaviour is not quite correct.  we want it to stop sending commands to grbl, clear the buffer,
        and send a new set of commands to grbl.  this would be a retract, stop spindle, extend locating bar,
        and release all clamps

        :return:
        """
        self.grbl_stream.send_direct_command("g90", clr_buffer=True)
        self.grbl_stream.send_direct_command("g0y0", clr_buffer=True)
        time.sleep(1)  # i couldn't get it to work without a pause,  can you add a real qt timer here?
        self.grbl_stream.add_new_command('g90')
        self.grbl_stream.add_new_command('g0y0')
        self.grbl_stream.add_new_command('g0z0')
        self.spindle_off()
        self.extend_locating_bar()
        self.release_clamp_right_vertical()
        self.release_clamp_left_vertical()
        self.release_clamp_right_horizontal()
        self.release_clamp_left_horizontal()

    def reset_machine(self):
        module_logger.debug("reset the machine")
        self.grbl_stream.send_direct_command(chr(0x85), clr_buffer=True)
        self.turn_off_machine()
        self.__rest_timer.start(2000)

    def turn_on_machine_after_reset(self):
        self.turn_on_machine()
        self.grbl_stream.add_new_command("$H")
        self.grbl_stream.add_new_command("g10 p0 l20 x0 y0 z0", notify_message='Homing Complete-Ready')
        self.set_wco()

    def turn_on_machine(self):
        module_logger.debug("turn on the machine")
        self.servoStartSignal.emit(True)

    def turn_off_machine(self):
        module_logger.debug("turn off the machine")
        self.servoStartSignal.emit(False)

    def set_wco(self):
        x_zero = CustomMachineParamManager.get_value("machine_x_zero")
        y_zero = CustomMachineParamManager.get_value('machine_y_zero')
        s1_x = CustomMachineParamManager.get_value("sander1_x_value")
        s1_y = CustomMachineParamManager.get_value("sander1_y_value")
        s2_x = CustomMachineParamManager.get_value("sander2_x_value")
        s2_y = CustomMachineParamManager.get_value("sander2_y_value")
        s3_x = CustomMachineParamManager.get_value("sander3_x_value")
        s3_y = CustomMachineParamManager.get_value("sander3_y_value")
        s4_x = CustomMachineParamManager.get_value("sander4_x_value")
        s4_y = CustomMachineParamManager.get_value("sander4_y_value")
        self.grbl_stream.add_new_command("g10 p1 l20 x0 y0 z0",
                                         notify_message='Homing Complete-Ready')
        self.grbl_stream.add_new_command(f'g10 p2 l20 x{x_zero - s1_x}y0z{y_zero - s1_y}')
        self.grbl_stream.add_new_command(f'g10 p3 l20 x{x_zero - s2_x}y0z{y_zero - s2_y}')
        self.grbl_stream.add_new_command(f'g10 p4 l20 x{x_zero - s3_x}y0z{y_zero - s3_y}')
        self.grbl_stream.add_new_command(f'g10 p5 l20 x{x_zero - s4_x}y0z{y_zero - s4_y}')

    def reset_and_home(self):
        self.grbl_stream.add_new_command('$slp')
        self.grbl_stream.add_new_command(chr(0x18), wait_after=2, notify_message="Homing")
        self.grbl_stream.add_new_command(chr(0x18), wait_after=2, notify_message="Homing")
        self.grbl_stream.add_new_command("")
        self.grbl_stream.add_new_command("$H")
        self.grbl_stream.add_new_command("g10 p0 l20 x0 y0 z0",
                                         notify_message='Homing Complete-Ready')
        self.set_wco()

        # todo, make it set the x,y zero from settings
        # todo, set up the offsets from settings. we also need to apply these at machine startup, and when the settings are saved

    def measure_tool(self):
        self.__measure_prob_counter = 0
        self.__retrieved_z_values.clear()

        def probe():
            self.grbl_stream.add_new_command('g0z3')  # retract 3 mm
            self.grbl_stream.add_new_command('g38.2z-3f50',
                                             notify_message="emit_measure_response")  # probe with error return, 3mm, feed 50mm/m

        self.grbl_stream.add_new_command('g90')  # switch to absolute units
        self.grbl_stream.add_new_command('g0z0')  # move z to zero to make sure we are clear of probe sensor
        self.grbl_stream.add_new_command('g0x0y0')  # move to x zero, y zero, starting position underneath probe sensor
        self.spindle_on()  # turn spindle on,  using line break sensor, we need bit spining to ensure we are getting accurate measure of tool
        self.grbl_stream.add_new_command('g38.2z-60f150')  # probe on, z 35mm, feed speed of 150mm/m
        self.grbl_stream.add_new_command('g91')  # switch to incremental units
        probe()  # perform slow probe cycle
        probe()  # repeat for consistent results
        probe()  # repeat again
        self.grbl_stream.add_new_command('g90')  # switch back to absolute units
        self.grbl_stream.add_new_command('g0z0', notify_message='Measuring complete')  # retract z back to 0
        self.spindle_off()  # turn spindle back off

    def change_machine_bit(self):
        self.park()
        # open dialog and have the user select what bit they would like to load, then tell them to load the bit
        # once they confirm they have completed changing the bit, we will measure the tool
        self.measure_tool()

    def check_events(self):
        total_num_of_holes = 0
        total_num_of_dowels = 0
        axis_value_changed_flag = False
        x_offset, y_offset, z_offset, a_offset = 0, 0, 0, 0
        cur_date = datetime.datetime.now().date()
        while not self.__event_queue.empty():
            event = self.__event_queue.get()
            if event.get("type") == "received_response" and event.get("value") == "emit_measure_response":
                response = event.get("response")
                response = response.lower()
                print(response)
                if response.startswith("[prb:"):
                    axis_values_str = response.split(":")[1].split(",")
                    print(axis_values_str)
                    if len(axis_values_str) == 5:
                        try:
                            z_value = float(axis_values_str[2])
                            self.__retrieved_z_values.append(z_value)
                        except Exception as e:
                            print(e)
                        self.__measure_prob_counter += 1
                        if self.__measure_prob_counter == 3:
                            self.__retrieved_z_values.sort()
                            CustomMachineParamManager.set_value("loaded_bit_length", self.__retrieved_z_values[0], True)
                            self.newBitLengthCaptured.emit(self.__retrieved_z_values[0])


            elif event.get("type") == "notification":
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
        self.spindle_on()
        self.machineStateChangedSignal.emit("pending- cycle 1")
        self.clamp_right_vertical()
        self.clamp_left_vertical()
        self.retract_locating_bar()
        print('you pressed start 1')

    def cycle_start_2(self):
        print('you pressed start 2')
        self.machineStateChangedSignal.emit("pending- cycle 2")
        self.clamp_right_horizontal()
        self.clamp_left_horizontal()
        # @ToDo generate grbl code
        # this is where the dovetail_code_generate will need to be called
        # then we need to send the g-code to grbl
        from models.dovetail_code_generator_new import GenerateCode
        grbl_generator = GenerateCode()
        grbl_generator.calculate()
        g_code = grbl_generator.g_code  # this already a list of commands
        for cmd in g_code:
            print(f"debug {cmd}")
            self.grbl_stream.add_new_command(cmd)
        self.extend_locating_bar()
        self.release_clamp_right_horizontal()
        self.release_clamp_left_horizontal()
        self.release_clamp_left_vertical()
        self.release_clamp_right_vertical()
        self.machineStateChangedSignal.emit('ready')
        time_to_run = self.calculate_run_time()
        self.machineStartedSignal.emit(time_to_run)

    def release_clamp_left_vertical(self):
        module_logger.debug('releasing left vertical clamp')
        self.grbl_stream.add_new_command('m65')

    def release_clamp_right_vertical(self):
        module_logger.debug('releasing right vertical clamp')
        self.grbl_stream.add_new_command('m67')

    def clamp_left_vertical(self):
        module_logger.debug('clamping left vertical')
        self.grbl_stream.add_new_command('m64')

    def clamp_right_vertical(self):
        module_logger.debug('clamping right vertical')
        self.grbl_stream.add_new_command('m66')

    def retract_locating_bar(self):
        module_logger.debug('retracting locating bar')
        self.grbl_stream.add_new_command('m63')

    def extend_locating_bar(self):
        module_logger.debug('extending locating bar')
        self.grbl_stream.add_new_command('m62')

    def clamp_right_horizontal(self):
        self.grbl_stream.add_new_command('m70')

    def release_clamp_right_horizontal(self):
        self.grbl_stream.add_new_command('m71')

    def clamp_left_horizontal(self):
        self.grbl_stream.add_new_command('m68')

    def release_clamp_left_horizontal(self):
        self.grbl_stream.add_new_command('m69')

    def update_machine_profiles(self, joint_profile, bit_profile, dowel_profile):
        self.__current_dowel_profile = dowel_profile
        self.__current_bit_profile = bit_profile
        self.__current_joint_profile = joint_profile

    def release_resources(self):
        self.deactivate_solenoids()
        self.spindle_off()
        self.turn_off_machine()
        self.grbl_stream.close_service()
