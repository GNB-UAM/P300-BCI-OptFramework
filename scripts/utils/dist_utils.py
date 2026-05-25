'''
This module will define some utilities regarding
probability distributions' functions estimation.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 19/09/2025
'''

import enum


class DistMode(enum.Enum):
    '''
    This enumeration defines the operation
    mode. When specified, it will fix several
    values of the specified dimension and estimate
    the expected values of the opposite's conditioned
    distribution.
    '''
    ObtainedAcc = "ObtainedAccuracies"
    RequiredTri = "RequiredTrials"

    def __str__(self):
        return self.value
