import enum
from constants import HOFF_SUBJECTS


class HoffElect(enum.Enum):
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
    M1 = 32
    M2 = 33


# ============== Hoffmann ==============
# Electrodes' sets
HOFF_ALL = {subject_nr: list(
    range(32)) for subject_nr in HOFF_SUBJECTS}

# See https://www.sciencedirect.com/science/article/abs/pii/S0165027007001094
HOFF_ONE = {subject_nr: [
    HoffElect.PZ.value
] for subject_nr in HOFF_SUBJECTS}

HOFF_TWO = {subject_nr: [
    HoffElect.PZ.value, HoffElect.CZ.value,
] for subject_nr in HOFF_SUBJECTS}

HOFF_FOUR = {subject_nr: [
    HoffElect.PZ.value, HoffElect.CZ.value,
    HoffElect.FZ.value, HoffElect.OZ.value,
] for subject_nr in HOFF_SUBJECTS}

HOFF_EIGHT = {subject_nr: [
    HoffElect.PZ.value, HoffElect.CZ.value,
    HoffElect.FZ.value, HoffElect.OZ.value,
    HoffElect.P3.value, HoffElect.P4.value,
    HoffElect.P7.value, HoffElect.P8.value
] for subject_nr in HOFF_SUBJECTS}

HOFF_SIXTEEN = {subject_nr: [
    HoffElect.PZ.value, HoffElect.CZ.value,
    HoffElect.FZ.value, HoffElect.OZ.value,
    HoffElect.P3.value, HoffElect.P4.value,
    HoffElect.P7.value, HoffElect.P8.value,
    HoffElect.O1.value, HoffElect.O2.value,
    HoffElect.CP1.value, HoffElect.CP2.value,
    HoffElect.C3.value, HoffElect.C4.value,
    HoffElect.FC1.value, HoffElect.FC2.value,
] for subject_nr in HOFF_SUBJECTS}

ELECT_SETS = {
    "Custom": None,
    "Hoffmann 1 set": HOFF_ONE,
    "Hoffmann 2 set": HOFF_TWO,
    "Hoffmann 4 set": HOFF_FOUR,
    "Hoffmann 8 set": HOFF_EIGHT,
    "Hoffmann 16 set": HOFF_SIXTEEN,
    "All": HOFF_ALL
}
