from enum import Enum


class AppSupportedOperations(Enum):
    dovetailCameraOperation = 0
    jointProfilesOperation = 1
    dowelsProfileOperation = 2
    bitProfilesOperation = 3
    restMachineOperation = 4
    settingParametersOperation = 5
    jointDowelBitProfilesOperation = 6
    partProfileOperation = 7
    sandingProgramsOperations = 8
    individualSandPaperOperations = 9
    sandingCameraOperations = 10
    doorStylesOperation = 11
    sandersManagementOperations = 12
    viewAccessDbOperation = 13


class AppSupportedSettingValues(Enum):
    standardWidth1 = 0
    standardWidth2 = 1
    standardWidth3 = 2
    standardWidth4 = 3


class WidgetsType(Enum):
    rangeWidget = 0
    boolWidget = 1
    textWidget = 2
    speedWidget = 3
    optionWidget = 4
    optionalRangeWidget = 5
    calculatedValue = 6
