import enum
from constants import WON_SUBJECTS


class WonElect(enum.Enum):
    '''
    This enumeration defines the
    loaded positions for every electrode.

    WARNING: Assuming no previous electrodes'
    selection have been made yet!
    '''
    FP1 = 0
    AF3 = 1
    F7 = 2
    F3 = 3
    FC1 = 4
    FC5 = 5
    T7 = 6
    C3 = 7
    CP1 = 8
    CP5 = 9
    P7 = 10
    P3 = 11
    PZ = 12
    PO3 = 13
    O1 = 14
    OZ = 15
    O2 = 16
    PO4 = 17
    P4 = 18
    P8 = 19
    CP6 = 20
    CP2 = 21
    C4 = 22
    T8 = 23
    FC6 = 24
    FC2 = 25
    F4 = 26
    F8 = 27
    AF4 = 28
    FP2 = 29
    FZ = 30
    CZ = 31


# ============== Won ==============
# Electrodes' sets
WON_ALL = {subject_nr: list(
    range(32)) for subject_nr in WON_SUBJECTS}

WON_ONE = {subject_nr: [
    WonElect.PZ.value
] for subject_nr in WON_SUBJECTS}

WON_TWO = {subject_nr: [
    WonElect.PZ.value, WonElect.CZ.value,
] for subject_nr in WON_SUBJECTS}

WON_FOUR = {subject_nr: [
    WonElect.PZ.value, WonElect.CZ.value,
    WonElect.FZ.value, WonElect.OZ.value,
] for subject_nr in WON_SUBJECTS}

WON_EIGHT = {subject_nr: [
    WonElect.PZ.value, WonElect.CZ.value,
    WonElect.FZ.value, WonElect.OZ.value,
    WonElect.P3.value, WonElect.P4.value,
    WonElect.P7.value, WonElect.P8.value
] for subject_nr in WON_SUBJECTS}

WON_SIXTEEN = {subject_nr: [
    WonElect.PZ.value, WonElect.CZ.value,
    WonElect.FZ.value, WonElect.OZ.value,
    WonElect.P3.value, WonElect.P4.value,
    WonElect.P7.value, WonElect.P8.value,
    WonElect.O1.value, WonElect.O2.value,
    WonElect.CP1.value, WonElect.CP2.value,
    WonElect.C3.value, WonElect.C4.value,
    WonElect.FC1.value, WonElect.FC2.value,
] for subject_nr in WON_SUBJECTS}

ELECT_SETS = {
    "Custom": None,
    "Won 1 set": WON_ONE,
    "Won 2 set": WON_TWO,
    "Won 4 set": WON_FOUR,
    "Won 8 set": WON_EIGHT,
    "Won 16 set": WON_SIXTEEN,
    "All": WON_ALL
}
