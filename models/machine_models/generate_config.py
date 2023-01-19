from configurations.custom_pram_loader import CustomMachineParamManager

MAX_WAIT_TIME = 30  # 20 sec
feed_speed_max = 15000  # we probably want to move this to a static config file
x_max_length = CustomMachineParamManager.set_value("x_max_length", 1778, auto_store=True)
y_max_width = CustomMachineParamManager.set_value("y_max_width", 660.4, auto_store=True)
sander_on_delay = .75  # we probably want to move this to a static config file
sander_off_delay = 3  # we probably want to move this to a static config file

sander_dictionary = {1: {'on': 'm62', 'off': 'm63', 'extend': 'm70', 'retract': 'm71', 'offset': 'g55'},
                     2: {'on': 'm64', 'off': 'm65', 'extend': 'm72', 'retract': 'm73', 'offset': 'g56'},
                     3: {'on': 'm66', 'off': 'm67', 'extend': 'm74', 'retract': 'm75', 'offset': 'g57'},
                     4: {'on': 'm68', 'off': 'm69', 'extend': 'm78', 'retract': 'm79', 'offset': 'g58'}
                     }
