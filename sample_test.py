import serial
import time
serial_dev = serial.Serial("/det/ttyACM0", 115200, timeout=0.5)

commands = ['g21g54(set units and wco)']

for command in commands:
    cmd_str = command + "\n"
    print(f"{cmd_str} sent to the machine ........")
    cmd_bytes = serial_dev.write(cmd_str.encode())
    time.sleep(0.5)
    rec_bytes_list = serial_dev.readlines()
    print(rec_bytes_list)
    print("#"*20)
