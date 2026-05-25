'''
This module will define some constant values.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 02/02/2024
'''
import enum
import numpy as np

SEED = 1234

# ============== Hoffmann ==============
HOFF_SFREQ = 2048

HOFF_NORMAL_TRIAL_EPOCHS = 5
HOFF_ANOMAL_TRIAL_EPOCHS = 1
HOFF_TRIAL_EPOCHS = HOFF_NORMAL_TRIAL_EPOCHS +\
    HOFF_ANOMAL_TRIAL_EPOCHS
HOFF_RUN_TRIALS = 20
# @hoffmann_efficient_2008 stimulus intervals in ms
HOFF_FLD = 100
HOFF_ISI = 300
HOFF_SOA = HOFF_ISI + HOFF_FLD

# Subject 5 is not included
HOFF_SUBJECTS = list(range(1, 5)) +\
    list(range(6, 9 + 1))
HOFF_SESSIONS = list(range(1, 4 + 1))
HOFF_RUNS = list(range(1, 6 + 1))
HOFF_DAY_SESSIONS = 2
HOFF_DAYS = [1, 2]

HOFF_STIM_LABELS = [
    "ST1", "ST2", "ST3",
    "ST4", "ST5", "ST6"
]

# ============== Won ==============
WON_SFREQ = 512

WON_NORMAL_TRIAL_EPOCHS = 10
WON_ANOMAL_TRIAL_EPOCHS = 2
WON_TRIAL_EPOCHS = WON_NORMAL_TRIAL_EPOCHS +\
    WON_ANOMAL_TRIAL_EPOCHS
WON_RUN_TRIALS = 15
# @won_eeg_2022 inter-stimulus interval in ms
WON_FLD = 125
WON_ISI = 62.5
WON_SOA = WON_FLD + WON_ISI

WON_SUBJECTS = list(range(1, 55 + 1))
WON_SESSIONS = list(range(1, 6 + 1))
WON_RUNS = list(range(1, 5 + 1))

WON_STIM_LABELS = [
    "R1", "R2", "R3", "R4", "R5", "R6",
    "C1", "C2", "C3", "C4", "C5", "C6"
]
# ============== ESS modes ==============


class ESSMode(enum.Enum):
    '''
    This enumeration defines the
    Early Stop Strategies available
    modes.
    '''
    RSVP = 0
    RCP_UNIF = 1
    RCP_AS_RSVP = 2


# ============== More utilities ==============
DATASETS = {
    "Hoffmann": {
        "ess_mode": ESSMode.RSVP,
        "sfreq": HOFF_SFREQ,
        "n_stimulus": HOFF_TRIAL_EPOCHS,
        "stimulus_labels": HOFF_STIM_LABELS,
        "n_trials": HOFF_RUN_TRIALS,
        "isi_secs": HOFF_ISI / 1e3,
        "soa_secs": HOFF_SOA / 1e3,
        "subjects": HOFF_SUBJECTS,
        "sessions": HOFF_SESSIONS,
        "runs_ids": np.repeat(
            np.arange(len(HOFF_SESSIONS)), len(HOFF_RUNS)),
        "n_targets": 1,
        "trial_secs": HOFF_SOA * HOFF_TRIAL_EPOCHS / 1e3,
    },
    "Won": {
        "ess_mode": ESSMode.RCP_UNIF,
        "sfreq": WON_SFREQ,
        "n_stimulus": WON_TRIAL_EPOCHS,
        "stimulus_labels": WON_STIM_LABELS,
        "n_trials": WON_RUN_TRIALS,
        "isi_secs": WON_ISI / 1e3,
        "soa_secs": WON_SOA / 1e3,
        "subjects": WON_SUBJECTS,
        "sessions": WON_SESSIONS,
        "runs_ids": np.repeat(
            np.arange(len(WON_SESSIONS)), len(WON_RUNS)),
        "n_targets": 2,
        "trial_secs": WON_SOA * WON_TRIAL_EPOCHS / 1e3
    }
}
DATASETS["WonRCP2RSVP"] = DATASETS["Won"].copy()
DATASETS["WonRCP2RSVP"]["ess_mode"] = ESSMode.RCP_AS_RSVP

# Aesthetics
FONT_SIZE = 30
COLORS_OS = [
    "#3274A1",  # ITR
    "#E1812C",  # ¾Gain + ¼Cons
    "#3A923A",  # ½Gain + ½Cons
    "#C03D3E"   # ¼Gain + ¾Cons
]


# Optimization strategies
OPTIM_STRATEGIES = {
    "ITR": "itr",
    "¼Gain + ¾Cons": (1/4, 3/4),
    "½Gain + ½Cons": (1/2, 1/2),
    "¾Gain + ¼Cons": (3/4, 1/4),
    "Custom GCB": "Custom GCB"
}

FRACTION_TO_ALPHA = {
    "ITR": "ITR",
    "¾Gain + ¼Cons": "GCB(α=0.75)",
    "½Gain + ½Cons": "GCB(α=0.50)",
    "¼Gain + ¾Cons": "GCB(α=0.25)"
}
