import serial
import time

class ProbCalibration(object):
    def __init__(self):
        self.serial_dev = serial.Serial("/dev/ttyACM0", 115200, timeout=0.5)

    def send_command(self, cmd:str, decode:bool=False, delay:float=0.5):
        result = None
        cmd_str = cmd + "\r\n"
        print(f"{cmd_str} sent to the machine ........")
        cmd_bytes = self.serial_dev.write(cmd_str.encode())
        time.sleep(delay)
        rec_bytes_list = self.serial_dev.readlines()
        if decode:
            result = ProbCalibration.decode_response(rec_bytes_list)
        return result

    def prob_calibration_seq(self, probe_x_zero, probe_y_zero):
        self.send_command('$h', delay=5)
        self.send_command('g21g54(set units and wco)')
        self.send_command(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}'
                          , delay=5)

        response = self.send_command('g38.5z-700f1200', delay=5, decode=True)
        if response is None:
            print("Failed to calibrate the prob")
            return False


        self.g_code.append(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        # self.g_code.append('g38.5x0f1200')
        # @TODO check if this will work
        # [b'[PRB:-137.018,0.000,-623.444:1]\r\n', b'ok\r\n', b'ok\r\n']
        cmd = {"cmd": 'g38.5x0f1200', "wait_time": 0.5, "notify_message": ""}
        response = self.serial_interface.grbl_stream.wait_for_response(cmd)
        print(response)
        result_x_minus = -59.997  # todo this will be replaced with result from probe
        self.g_code.append(f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        self.g_code.append(f'g38.5z-{self.starting_rough[1] + 10}')
        result_z_plus = -623.969  # todo get return of probe
        self.g_code.append(
            f'g0x-{self.starting_rough[0] + self.cal_size[0] - self.offset_in}z-{self.starting_rough[1] - self.offset_in}')
        self.g_code.append(f'g38.5x-1700')
        result_x_plus = -805.910  # todo get return of probe
        self.g_code.append(
            f'g0x-{self.starting_rough[0] + self.offset_in}z-{self.starting_rough[1] - self.cal_size[1] + self.offset_in}')
        self.g_code.append('g38.5z0')
        result_z_minus = -334.933  # todo get return of probe
        result_size = -1 * (result_x_plus - result_x_minus), result_z_minus - result_z_plus
        CustomMachineParamManager.set_value("probe_diameter", round(mean((self.cal_size[0] - result_size[0],
                                                                          self.cal_size[1] - result_size[1])),
                                                                    3), auto_store=True)
        CustomMachineParamManager.set_value('probe_x_zero', (-1 * result_x_minus) - CustomMachineParamManager.get_value(
            'probe_diameter'), auto_store=True)
        CustomMachineParamManager.set_value('probe_y_zero', (-1 * result_z_plus) + CustomMachineParamManager.get_value(
            'probe_diameter'), auto_store=True)


        return True



if __name__ == "__main__":
    p = ProbCalibration()
    is_calibrated = p.prob_calibration_seq(0, 0)
