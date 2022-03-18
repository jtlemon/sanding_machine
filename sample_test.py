import serial
import time
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
serial_dev = serial.Serial("/dev/ttyACM0", 115200, timeout=0.5)

commands = [('$h', 10, False),('g21g54(set units and wco)', 0, False), ('g0x-135z-615', 5, False), ('g38.5z-700f1200', 5, True)]
for command, delay, decode_result in commands:
    cmd_str = command + "\r\n"
    print(f"{cmd_str} sent to the machine ........")
    cmd_bytes = serial_dev.write(cmd_str.encode())
    time.sleep(delay)
    time.sleep(0.5)
    rec_bytes_list = serial_dev.readlines()
    if decode_result is True:
        result = decode_response(rec_bytes_list)
        if result is not None:
            print(result)
        else:
            print("failed to decode the response")

    print("#"*20)
