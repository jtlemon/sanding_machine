from .sander_probe import Probe


def turn_vacuum_on(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_on(ch)
    else:
        pass
        # print(f"debug mode turn on vacuum {ch}")


def turn_vacuum_off(sensors_board_ref, ch):
    if sensors_board_ref is not None:
        sensors_board_ref.turn_vacuum_off(ch)
    else:
        # print(f"debug mode turn off vacuum {ch}")
        pass


def probe_test():
    all_g_codes = []
    generate_probe = Probe()
    all_g_codes.extend(generate_probe.calibrate())
    print(all_g_codes, sep="\n")
    print(generate_probe.probe_part())


def end_cycle(self):
    buffer = []
    buffer.append('m5(deactivate vacuum)')
    buffer.append('g54(reset wco)')
    buffer.append(f'g0x-900y0(go to park position)')
    return buffer
