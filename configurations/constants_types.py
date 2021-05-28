from enum import Enum


class AppSupportedOperations(Enum):
    dovetailCameraOperation = 0
    jointProfilesOperation = 1
    feedAndSpeedOperation = 2
    restMachineOperation = 3
    settingParametersOperation = 4


class AppSupportedSettingValues(Enum):
    standardWidth1 = 0
    standardWidth2 = 1
    standardWidth3 = 2
    standardWidth4 = 3

class WidgetsType(Enum):
    rangeWidget = 0
    boolWidget = 1