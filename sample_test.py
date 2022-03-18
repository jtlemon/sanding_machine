import serial
import time
serial_dev = serial.Serial("/dev/ttyACM0", 115200, timeout=0.5)

commands = [('$h', 10),('g21g54(set units and wco)', 0), ('g0x-135z-615', 5), ('g38.5z-700f1200', 5)]

for command, delay in commands:
    cmd_str = command + "\r\n"
    print(f"{cmd_str} sent to the machine ........")
    cmd_bytes = serial_dev.write(cmd_str.encode())
    time.sleep(delay)
    time.sleep(0.5)
    rec_bytes_list = serial_dev.readlines()
    print(rec_bytes_list)
    print("#"*20)
