from enum import Enum


class AppSupportedOperations(Enum):
    jointSettingOperation = 0
    feedAndSpeedOperation = 1
    restMachineOperation = 2
    settingParametersOperation = 3


class AppSupportedSettingValues(Enum):
    standardWidth1 = 0
    standardWidth2 = 1
    standardWidth3 = 2
    standardWidth4 = 3

class SupportedMachines(Enum):
    dovetailMachine = 0
    drillDowelMachine = 1