'''
This module will define some utilites
when splitting the data.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 15/02/2024
'''

import numpy as np
from typing import List


def get_sbj_runs_ids(
        n_sessions: int,
        n_runs: int) -> np.ndarray:
    '''
    This method will return a list with each
    run's identifiers.

    Warning: This method will assume that runs from
    the same session are contiguous.

    Example:
    ```
    get_sbj_runs_ids(4, 6)
    ----- Output -----
    array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3,
       3, 3])
    ```

    :param n_sessions: Number of sessions per subject.
    :param n_runs: Number of runs per session.
    :return np.ndarray: Array with the runs' identifiers.
    '''
    return np.repeat(
        np.arange(n_sessions), n_runs)


def index_data(
        idxs: np.ndarray,
        *args: List[np.ndarray]) -> List[np.ndarray]:
    '''
    This method will index a list of arrays
    with the specified identifiers.

    :param idxs: 1D-Array with the identifiers.
    :param args: List of arrays.
    :return List[np.ndarray]: List
    with the indexed arrays.
    '''
    return list(map(lambda x: x[idxs], args))
