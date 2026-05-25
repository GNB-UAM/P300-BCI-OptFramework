'''
This module will contain multiple
metrics such as classifier metrics,
BCI metrics, ...

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 04/02/2024
'''

import math
import numpy as np
from typing import Tuple


def itr(n_classes: int,
        clf_acc: float,
        trial_secs: float) -> float:
    '''
    This method will compute the Information
    Transfer Rate of a classifier from its
    accuracy, number of choices, and prediction
    time of one trial.

    Example:
    ```
    itr(n_classes=6, clf_acc=.5, trial_secs=2)
    ----- Output -----
    12.719953598324249
    ```

    :param n_classes: Classifier's number of choices,
    or number of the problem's classes.
    :param clf_acc: Classifier's accuracy.
    :param trial_secs: One trial's prediction
    time in seconds.

    :return float: Information Transfer Rate metric
    in bits/min.
    '''
    if clf_acc >= 1:
        clf_acc = .999
    elif clf_acc <= 0:
        return 0

    return (60/trial_secs) * (
        math.log2(n_classes) +
        clf_acc * math.log2(clf_acc) + (1 - clf_acc) *
        math.log2((1 - clf_acc)/(n_classes - 1)))


def bci_utility(
        n_classes: int,
        clf_acc: float,
        trial_secs: float) -> float:
    '''
    This method will compute the BCI-Utility
    metric of a classifier from its accuracy,
    number of choices, and prediction time of
    one trial.

    Example:
    ```
    bci_utility(n_classes=6, clf_acc=.6, trial_secs=2)
    ----- Output -----
    13.93156856932417
    ```

    :param n_classes: Classifier's number of choices,
    or number of the problem's classes.
    :param clf_acc: Classifier's accuracy.
    :param trial_secs: One trial's prediction
    time in seconds.

    :return float: BCI-Utility metric in bits/min.
    '''
    if clf_acc <= 0.5:
        return 0
    else:
        return (60/trial_secs) * (
            (2*clf_acc - 1) *
            (math.log2(n_classes - 1))
        )


def spm(
        n_classes: int,
        clf_acc: float,
        trial_secs: float) -> float:
    '''
    This method will compute the Symbols
    Per Minute of a classifier from its
    accuracy, number of choices, and prediction
    time of one trial.

    WARNING: The number of classes parameter is
    not used, this metric will correspond with
    a control interface instead of a speller,
    i.e. it can only make a decission within the
    `trial_secs` range. In other words, the number
    of decissions per minute is `(1/trial_secs)*(60s/1min)`.

    Example:
    ```
    spm(n_classes=6, clf_acc=.6, trial_secs=2)
    ----- Output -----
    5.999999999999998
    ```

    :param n_classes: Classifier's number of choices,
    or number of the problem's classes.
    :param clf_acc: Classifier's accuracy.
    :param trial_secs: One trial's prediction
    time in seconds.

    :return float: Symbols per minute.
    '''
    correct_percent = clf_acc
    incorrect_percent = 1 - clf_acc
    decs_per_min = (1/trial_secs) * 60  # From secs to mins

    return decs_per_min * (
        correct_percent - incorrect_percent)


def gcb(
        gain: np.array,
        cons: np.array,
        weights: Tuple[float, float],
        acc_base: float = None,
        t_base: int = None) -> np.array:
    '''
    This method will compute the Gain-Cons balance.

    :param gain: 1-D Gain measures.
    :param cons: 1-D Conservation measures.
    :param weights: Tuple with the weights for both
    gain and cons measures.
    :param t_base: Unused (added to use it as an interface
    of `bcim_gc`).
    :param acc_base: Unused (added to use it as an interface
    of `bcim_gc`).

    :return np.array: 1-D array with the Gain-Cons balance.
    '''
    return weights[0] * gain + weights[1] * cons


def bcim_gc(
        gain: np.array,
        cons: np.array,
        measure: callable,
        t_base: int,
        acc_base: float,
        n_classes: int,
        trial_secs: float) -> np.array:
    '''
    This method will compute a BCI measure given
    the Gain and Conservation measures.

    :param gain: 1-D Gain measures.
    :param cons: 1-D Conservation measures.
    :param measure: BCI measure to compute, expected
    header: `measure(n_classes, clf_acc, trial_sec)`
    :param t_base: Baseline number of trials consumed.
    :param acc_base: Baseline accuracy.
    :param n_classes: Classifier's number of choices,
    or number of the problem's classes.
    :param trial_secs: Number of seconds per trial.
    '''
    # Inverse of both Gain & Cons measures
    t_star = t_base - gain * t_base
    acc_star = (cons - 1) * acc_base + acc_base

    return measure(n_classes, acc_star, t_star * trial_secs)
