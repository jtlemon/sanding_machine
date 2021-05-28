from enum import Enum


class AppSupportedOperations(Enum):
    dovetailCameraOperation = 0
    jointProfilesOperation = 1
    dowelsProfileOperation = 2
    feedAndSpeedOperation = 3
    restMachineOperation = 4
    settingParametersOperation = 5


class AppSupportedSettingValues(Enum):
    standardWidth1 = 0
    standardWidth2 = 1
    standardWidth3 = 2
    standardWidth4 = 3

class WidgetsType(Enum):
    rangeWidget = 0
    boolWidget = 1