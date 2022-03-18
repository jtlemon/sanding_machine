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
        self.send_command('g0x-135z-615', delay=5)
        response = self.send_command('g38.5z-700f1200', delay=5, decode=True)
        if response is None:
            print("Failed to calibrate the prob")
            return False
        return True

    @staticmethod
    def decode_response(response_list):
        values = None
        for rec_bytes in response_list:
            rec_str = rec_bytes.decode()
            rec_str = rec_str.rstrip("\r\n")
            # [b'[PRB:-137.018,0.000,-623.444:1]\r\n', b'ok\r\n', b'ok\r\n']
            if "PRB:" in rec_str:
                sub_str = rec_str[5:-3].split(",")
                values = [float(val) for val in sub_str]
        return values

if __name__ == "__main__":
    p = ProbCalibration()
    is_calibrated = p.prob_calibration_seq(0, 0)
