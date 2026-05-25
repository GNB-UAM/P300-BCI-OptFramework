'''
This module will define some utilities
to perform multiple early stop criterias
over an array with predictions and shape:
    (n_runs, n_trials, n_flashes)

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 06/04/2024
'''

from __future__ import annotations
import numpy as np
from constants import ESSMode
from functools import partial
from scipy.stats import ttest_ind
from abc import ABC, abstractmethod
from voting_utils import (sort_stim,
                          soft_voting)
from typing import Union, Tuple, Dict, Any


class EarlyStop(ABC):
    '''
    This class will be used as interface for other
    early stop strategies.

    :param mode: ESSMode indicating paradigm type.
    :param n_flashes: Number of flashes of the experiment.
    '''

    MODES = list(ESSMode.__members__.values())
    N_IT = {
        ESSMode.RSVP: 1,
        ESSMode.RCP_UNIF: 2,
        ESSMode.RCP_AS_RSVP: 2
    }

    def __init__(self, mode: ESSMode, n_flashes: int) -> EarlyStop:
        if mode not in self.MODES:
            raise Exception(f"Mode {self.mode} is invalid!")
        self.mode = mode
        self.n_flashes = n_flashes
        self.n_it = self.N_IT[mode]
        self.is_fitted_ = False

    @staticmethod
    def gain(bline: EarlyStop, strat: EarlyStop,
             y: np.array, stim_seq: np.ndarray,
             return_extra: bool = False) -> Union[float, Tuple[float]]:
        '''
        This method compares a baseline early stop strategy
        against another strategy to determine the speed Gain
        within a specific problem.

        :param bline: Baseline early stop strategy.
        :param strat: Early stop strategy.
        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param return_extra: Whether to also include the
        expected trial at which the strategies would have
        stopped in the return statement:
        `(gain, trial_baseline, trial_strategy)`

        :return Union[float, Tuple[float]]: Speed gain and
        the trials at which the baseline and the proposed strategies
        would have stopped (if `return_extra` is provided).
        '''
        stop_bline = bline.avg_stop(y, stim_seq)
        stop_strat = strat.avg_stop(y, stim_seq)

        gain = (stop_bline - stop_strat)/max(stop_bline, 1)  # error control

        if return_extra:
            return (gain, stop_bline, stop_strat)
        else:
            return gain

    @staticmethod
    def cons(bline: EarlyStop, strat: EarlyStop,
             y: np.array, stim_seq: np.ndarray,
             z: np.ndarray, return_extra: bool = False) -> Union[float,
                                                                 Tuple[float]]:
        '''
        This method compares a baseline early stop strategy
        against another strategy to determine the accuracy
        Conservation within a specific problem.

        :param bline: Baseline early stop strategy.
        :param strat: Early stop strategy.
        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :param return_extra: Whether to also include the
        expected accuracy every strategy would have
        achieved in the return statement:
        `(cons, acc_baseline, acc_strategy)`

        :return Union[float, Tuple[float]]: Accuracy conservation and
        the trials at which the baseline and the proposed strategies
        would have stopped (if `return_extra` is provided).
        '''
        acc_bline = bline.score(y, stim_seq, z)
        acc_strat = strat.score(y, stim_seq, z)

        cons = 1 - (acc_bline - acc_strat) / \
            max(acc_bline, 1e-9)  # error control

        if return_extra:
            return (cons, acc_bline, acc_strat)
        else:
            return cons

    def _soft_voting(self, y: np.array,
                     stim_seq: np.ndarray) -> np.ndarray:
        '''
        Perform Soft-Voting.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Soft-voting permitted format
        with shape:
            (n_runs, n_trials, n_it, n_flashes/n_it)
        '''
        n_runs, n_epochs = stim_seq.shape
        n_trials = n_epochs // self.n_flashes

        # Reshape to have (n_runs, n_trials, n_flashes)
        y_res = y.reshape(n_runs, n_epochs)
        y_res = y_res.reshape(
            n_runs, n_trials, self.n_flashes)
        stim_seq_res = stim_seq.reshape(
            n_runs, n_trials, self.n_flashes)

        # Sort stimuli to perform Soft-Voting
        y_res = sort_stim(y_res, stim_seq_res)
        y_soft = soft_voting(y_res, mean_div=False)

        return y_soft.reshape(
            n_runs, n_trials, self.n_it,
            self.n_flashes // self.n_it
        )

    def _stat_test(self, y: np.array,
                   stim_seq: np.ndarray,
                   stat: callable) -> np.ndarray:
        '''
        Perform a OneVsRest statistical test to obtain
        the critical values from a matrix of evidences.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param stat: Statistical test to apply.
        :return np.array: p-values matrix with shape:
            (n_runs, n_trials, n_it, n_flashes/n_it)
        Being `n_flashes/n_it` the number of stimuli per
        intensification type (e.g. rows or columns).
        '''
        n_runs, n_epochs = stim_seq.shape
        n_trials = n_epochs // self.n_flashes
        n_flashes_it = self.n_flashes // self.n_it

        # Reshape to have (n_runs, n_trials, n_flashes)
        y_res = y.reshape(n_runs, n_epochs)
        y_res = y_res.reshape(
            n_runs, n_trials, self.n_flashes)
        stim_seq_res = stim_seq.reshape(
            n_runs, n_trials, self.n_flashes)

        # Sort & reshape stimuli to obtain p-values
        y_res = sort_stim(y_res, stim_seq_res).reshape(
            n_runs, n_trials, self.n_it, n_flashes_it)
        # (n_runs, n_it, n_trials, n_flashes_it)
        y_res = np.swapaxes(y_res, 1, 2)

        # Obtain p-values
        p_vals = np.ones_like(y_res)
        # Start at `2` to compare with, at least, two examples (`0` and `1`)
        for trial_nr in range(2, n_trials + 1):
            idx_trial = trial_nr - 1

            # (n_runs, n_it, :trial_nr, n_flashes_it)
            z = y_res[:, :, :trial_nr]

            for idx_flash in range(n_flashes_it):

                # Stimuli masks
                mask_ntgt = np.ones_like(z).astype(bool)
                # non-target mask — don't include the target
                mask_ntgt[..., idx_flash] = False
                # target mask
                mask_tgt = ~mask_ntgt

                # (n_runs, n_it, trials_seen x (n_flashes_it - 1))
                flash_ntgt = z[mask_ntgt].reshape(
                    n_runs, self.n_it, -1)
                # (n_runs, n_it, trials_seen x 1)
                flash_tgt = z[mask_tgt].reshape(
                    n_runs, self.n_it, -1)

                # OneVSRest
                p_vals[:, :, idx_trial, idx_flash] =\
                    stat(flash_tgt, flash_ntgt, axis=2).pvalue

        # Transform into original shape
        # (n_runs, n_it, n_trials, n_flashes_it) ->
        # (n_runs, n_trials, n_it, n_flashes_it)
        return np.swapaxes(p_vals, 1, 2)

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        '''
        This method will return the fitted
        parameters of this class.
        '''

    @abstractmethod
    def set_params(self, params):
        '''
        This method will set the model
        parameters.

        :param params: Model parameters.
        '''

    @abstractmethod
    def fit(self, y: np.array,
            stim_seq: np.ndarray,
            z: np.ndarray,
            bline: EarlyStop,
            measure: callable) -> EarlyStop:
        '''
        This method will fit the early stop algorithm
        in accordance to a particular measure.

        NOTE: The method will MAXIMISE the measure.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :param bline: Baseline early stop strategy to
        compute `gain` and `cons`.
        :param measure: Function with the following
        header: `measure(gain, cons, tbase, accbase)`
        '''
        if self.is_fitted_:
            print("Already fitted!")
            return self

    @abstractmethod
    def _stop_rsvp(self, y: np.array,
                   stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will select the trial with the
        most interesting stimuli to predict for each run
        assuming the paradigm employed was a Rapid Serial
        Visual Presentation, i.e. one target per trial
        and a single intensification type (only images, numbers, ...)

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Trials chosen at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''

    @abstractmethod
    def _stop_rcp_unif(self, y: np.array,
                       stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will select the trial with the
        most interesting stimuli to predict for each
        run assuming the paradigm employed was a
        Row-Column Paradigm, i.e. two targets per
        trial and a two intensification types (rows
        and columns).

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''

    def _stop_rcp_as_rsvp(self, y: np.array,
                          stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will select the trial with the
        most interesting stimuli to predict for each
        run assuming ignoring the paradigm employed was a
        Row-Column Paradigm and treating it as a regular
        RSVP instead.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''
        return self._stop_rcp_unif(y, stim_seq).reshape(-1, 1)

    def stop(self, y: np.array, stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will select the trial with the
        most interesting stimuli to predict.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Trials chosen at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''
        if self.mode == ESSMode.RSVP:
            return self._stop_rsvp(y, stim_seq)
        elif self.mode == ESSMode.RCP_UNIF:
            return self._stop_rcp_unif(y, stim_seq)
        elif self.mode == ESSMode.RCP_AS_RSVP:
            return self._stop_rcp_as_rsvp(y, stim_seq)

    def avg_stop(self, y: np.array, stim_seq: np.ndarray) -> int:
        '''
        This method will obtain the expected trial at which it
        would stop. Considering that different intensification
        types could stop at different trials, the strategy will
        wait until the highest trial is chosen.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return int: Expected trial chosen by the early
        stop strategy.
        '''
        trials = self.stop(y, stim_seq)

        # We wait until the final selection and then average
        return np.mean(np.max(trials, axis=1))

    def _predict_rsvp(self, y: np.array,
                      stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will predict the chosen stimuli
        for each run assuming the paradigm employed
        was a Rapid Serial Visual Presentation, i.e.
        one target per trial and a single intensification
        type (only images, numbers, ...)

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''
        n_runs, _ = stim_seq.shape
        runs_idxs = np.arange(n_runs)

        trials = self._stop_rsvp(
            y, stim_seq).squeeze() - 1  # -1 to make them indexes

        y_soft = self._soft_voting(y, stim_seq)
        y_soft_pred = y_soft[runs_idxs, trials]

        return np.argmax(y_soft_pred, axis=2)

    def _predict_rcp_unif(self, y: np.array,
                          stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will predict the chosen stimuli
        for each run assuming the paradigm employed
        was a Row-Column Paradigm, i.e. two targets
        per trial and a two intensification types
        (rows and columns).

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''
        n_runs, _ = stim_seq.shape
        runs_idxs = np.arange(n_runs)

        # We wait until the final selection
        trials = np.max(self._stop_rcp_unif(
            y, stim_seq), axis=1) - 1  # -1 to make them indexes

        y_soft = self._soft_voting(y, stim_seq)
        y_soft_pred = y_soft[runs_idxs, trials]

        z_pred = np.argmax(y_soft_pred, axis=2)
        # To distinguish rows from cols
        z_pred[:, 1] += self.n_flashes // self.n_it

        return z_pred

    def _predict_rcp_as_rsvp(self, y: np.array,
                             stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will predict the chosen stimuli
        for each run ignoring the paradigm employed
        was a Row-Column Paradigm and treating it as
        a regular RSVP instead.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, 1)
        '''
        return self._predict_rcp_unif(y, stim_seq).reshape(-1, 1)

    def predict(self, y: np.array, stim_seq: np.ndarray) -> np.ndarray:
        '''
        This method will predict the chosen stimuli
        for each run.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :return np.array: Stimulus predicted at run level
        for every intensification type with shape:
            (n_runs, n_it)
        '''
        if self.mode == ESSMode.RSVP:
            return self._predict_rsvp(y, stim_seq)
        elif self.mode == ESSMode.RCP_UNIF:
            return self._predict_rcp_unif(y, stim_seq)
        elif self.mode == ESSMode.RCP_AS_RSVP:
            return self._predict_rcp_as_rsvp(y, stim_seq)

    def _score_rsvp(self, y: np.array, stim_seq: np.ndarray, z: np.ndarray):
        '''
        This method will give a score of the predicted symbol
        per run with a regular accuracy measure. Please note
        that in RCP paradigms symbol (letter) != stimulus (flash).

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :return float: Accuracy score.
        '''
        n_tgts, _ = z.shape
        z_pred = self.predict(y, stim_seq)

        # Consider all intensification types to classify correctly
        return np.count_nonzero(np.all(
            z_pred == z, axis=1)) / n_tgts

    def _score_rcp(self, y: np.array, stim_seq: np.ndarray, z: np.ndarray):
        '''
        This method will give a score of the predicted symbol
        per run with a regular accuracy measure. Please note
        that in RCP paradigms symbol (letter) != stimulus (flash).

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :return float: Accuracy score.
        '''
        return self._score_rsvp(y, stim_seq, z)

    def _score_rcp_as_rsvp(self, y: np.array,
                           stim_seq: np.ndarray,
                           z: np.ndarray):
        '''
        This method will give a score of the predicted symbol
        per run with a regular accuracy measure. Please note
        that here we score at stimulus level.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :return float: Accuracy score.
        '''
        n_tgts = np.prod(z.shape)
        z_res = z.reshape(-1, 1)
        z_pred = self.predict(y, stim_seq)

        # Consider intensification types independently
        return np.count_nonzero(np.all(
            z_pred == z_res, axis=1)) / n_tgts

    def score(self, y: np.array, stim_seq: np.ndarray, z: np.ndarray) -> float:
        '''
        This method will give a score of the predicted symbol
        per run with a regular accuracy measure.

        :param y: Evidences with shape:
            (n_samples,)
        :param stim_seq: Stimulus sequence with shape:
            (n_runs, n_epochs)
        :param z: Ground-truth stimuli at run level for every
        intensification type with shape:
            (n_runs, n_it)
        :return float: Accuracy score.
        '''
        if self.mode == ESSMode.RSVP:
            return self._score_rsvp(y, stim_seq, z)
        elif self.mode == ESSMode.RCP_UNIF:
            return self._score_rcp(y, stim_seq, z)
        elif self.mode == ESSMode.RCP_AS_RSVP:
            return self._score_rcp_as_rsvp(y, stim_seq, z)


class FixedStop(EarlyStop):
    '''
    This class will simulate a fixed-stop criteria.

    :param mode: ESSMode indicating paradigm type.
    :param n_flashes: Number of flashes of the experiment.
    :param trial: Trial to stop at, defaults to `None`.
    '''

    def __init__(self, mode: ESSMode, n_flashes: int, trial: int = None):
        super().__init__(mode, n_flashes)

        if trial is not None:
            self.trial = trial
            self.is_fitted_ = True
        else:
            self.trial = None

    def _stop_rsvp(self, y: np.array,
                   stim_seq: np.ndarray) -> np.ndarray:
        n_runs, _ = stim_seq.shape
        return np.repeat(self.trial, n_runs)[:, np.newaxis]

    def _stop_rcp_unif(self, y: np.array,
                       stim_seq: np.ndarray) -> np.ndarray:
        n_runs, _ = stim_seq.shape

        return np.tile(
            (self.trial, self.trial), n_runs
        ).reshape(n_runs, self.n_it)

    def get_params(self) -> Dict[str, Any]:
        return {"trial": self.trial}

    def set_params(self, params):
        vals = list(map(lambda x: x["trial"], params))

        self.trial = round(np.mean(vals))
        self.is_fitted_ = True

    def fit(self, y: np.array,
            stim_seq: np.ndarray,
            z: np.ndarray,
            bline: EarlyStop,
            measure: callable) -> FixedStop:
        super().fit(y, stim_seq, z, bline, measure)

        _, n_epochs = stim_seq.shape
        n_trials = n_epochs // self.n_flashes

        measure_vals = np.zeros(n_trials)
        for idx, trial in enumerate(range(1, n_trials + 1)):
            self.trial = trial
            measure_vals[idx] = measure(
                gain=self.gain(bline, self, y, stim_seq),
                cons=self.cons(bline, self, y, stim_seq, z),
                t_base=bline.avg_stop(y, stim_seq),
                acc_base=bline.score(y, stim_seq, z)
            )

        # +1 because it is an index
        self.trial = int(np.argmax(measure_vals) + 1)
        self.is_fitted_ = True

        return self


class AccumEvid(EarlyStop):
    '''
    This class will simulate an accumulated evidence
    early stop criteria.

    :param mode: ESSMode indicating paradigm type.
    :param n_flashes: Number of flashes of the experiment.
    :param threshold: Threshold to surpass.
    '''

    def __init__(self, mode: ESSMode, n_flashes: int, threshold: float = None):
        super().__init__(mode, n_flashes)

        if threshold is not None:
            self.threshold = threshold
            self.is_fitted_ = True
        else:
            self.threshold = None

    def _stop_rsvp(self, y: np.array,
                   stim_seq: np.ndarray) -> np.ndarray:
        y_soft = self._soft_voting(y, stim_seq)
        _, n_trials, _, _ = y_soft.shape

        # Extract indexes of the first trials that
        # surpass the threshold.
        threshold_mask = np.any(y_soft >= self.threshold, axis=3)
        # +1 because they are indexes
        trials = np.argmax(threshold_mask, axis=1) + 1

        # When the threshold is not surpassed, we have
        # to stop at the last trial
        force_stop_runs, force_stop_its = np.where(
            ~threshold_mask[:, -1])
        trials[force_stop_runs, force_stop_its] = n_trials

        return trials

    def _stop_rcp_unif(self, y: np.array,
                       stim_seq: np.ndarray) -> np.ndarray:
        # The same as with RSVP
        return self._stop_rsvp(y, stim_seq)

    def get_params(self) -> Dict[str, Any]:
        return {"threshold": self.threshold}

    def set_params(self, params):
        vals = list(map(lambda x: x["threshold"], params))

        self.threshold = np.mean(vals)
        self.is_fitted_ = True

    def fit(self, y: np.array,
            stim_seq: np.ndarray,
            z: np.ndarray,
            bline: EarlyStop,
            measure: callable) -> AccumEvid:
        super().fit(y, stim_seq, z, bline, measure)

        _, n_epochs = stim_seq.shape
        n_trials = n_epochs // self.n_flashes

        thrs = np.linspace(
            .1, n_trials, n_trials*2)  # arbitrary thresholds to test

        measure_vals = np.zeros_like(thrs)
        for idx, thr in enumerate(thrs):
            self.threshold = thr
            measure_vals[idx] = measure(
                gain=self.gain(bline, self, y, stim_seq),
                cons=self.cons(bline, self, y, stim_seq, z),
                t_base=bline.avg_stop(y, stim_seq),
                acc_base=bline.score(y, stim_seq, z)
            )

        self.threshold = thrs[np.argmax(measure_vals)]
        self.is_fitted_ = True

        return self


class StatsTest(EarlyStop):
    '''
    This class will simulate a statistical test
    early stop criteria.

    NOTE: The statistical test to be executed will
    be Welch's T-test and the hypothesis to be tested:
    - The target's classifier scores have higher mean than
    the non-target ones (OneVsRest).

    :param mode: ESSMode indicating paradigm type.
    :param n_flashes: Number of flashes of the experiment.
    :param alpha: Significance level to surpass.
    :param bonf: Whether to apply Bonferroni's correction or
    not, default to `True`
    '''

    def __init__(self, mode: ESSMode, n_flashes: int,
                 alpha: float = None, bonf: bool = True):
        super().__init__(mode, n_flashes)

        if alpha is not None:
            self.alpha = alpha
            self.is_fitted_ = True
        else:
            self.alpha = None

        self.bonf = bonf
        self.stat = partial(ttest_ind, equal_var=False,
                            alternative="greater")

    def _stop_rsvp(self, y: np.array,
                   stim_seq: np.ndarray) -> np.ndarray:
        p_vals = self._stat_test(y, stim_seq, self.stat)\
            if self.is_fitted_ else self.p_vals
        n_runs, n_trials, _, n_flashes_it = p_vals.shape

        # Bonferroni correction
        n_tests = n_flashes_it
        alpha = self.alpha/n_tests\
            if self.bonf else self.alpha

        # Trials with significant stimuli
        # (n_runs, n_it)
        trials = (p_vals < alpha).any(
            axis=3).argmax(axis=1) + 1  # +1 because they are indexes!
        trials[(trials == 1)] = n_trials

        return trials

    def _stop_rcp_unif(self, y: np.array,
                       stim_seq: np.ndarray) -> np.ndarray:
        return self._stop_rsvp(y, stim_seq)

    def _predict_rsvp(self, y: np.array,
                      stim_seq: np.ndarray) -> np.ndarray:
        p_vals = self._stat_test(y, stim_seq, self.stat)\
            if self.is_fitted_ else self.p_vals
        n_runs, _, _, _ = p_vals.shape

        # Previously stopped trials — wait until the last selection.
        # (n_runs, n_it)
        stop_run = np.max(self._stop_rsvp(
            y, stim_seq), axis=1) - 1  # -1 to make them indexes

        # Stimuli with the lowest p-values per run
        return np.argmin(
            p_vals[np.arange(n_runs), stop_run], axis=-1)

    def _predict_rcp_unif(self, y: np.array,
                          stim_seq: np.ndarray) -> np.ndarray:
        z_pred = self._predict_rsvp(y, stim_seq)

        # To distinguish rows from cols
        z_pred[:, 1] += self.n_flashes // self.n_it

        return z_pred

    def get_params(self) -> Dict[str, Any]:
        return {"alpha": self.alpha}

    def set_params(self, params):
        vals = list(map(lambda x: x["alpha"], params))

        self.alpha = np.mean(vals)
        self.is_fitted_ = True

    def fit(self, y: np.array,
            stim_seq: np.ndarray,
            z: np.ndarray,
            bline: EarlyStop,
            measure: callable) -> StatsTest:
        super().fit(y, stim_seq, z, bline, measure)
        _, n_epochs = stim_seq.shape

        # arbitrary significance values to test
        a_vals = np.linspace(start=1e-3, stop=1, num=20)

        # training p-values
        self.p_vals = self._stat_test(
            y, stim_seq, self.stat)

        measure_vals = np.zeros(len(a_vals))
        for idx, a in enumerate(a_vals):
            self.alpha = a
            measure_vals[idx] = measure(
                gain=self.gain(bline, self, y, stim_seq),
                cons=self.cons(bline, self, y, stim_seq, z),
                t_base=bline.avg_stop(y, stim_seq),
                acc_base=bline.score(y, stim_seq, z)
            )

        self.alpha = a_vals[np.argmax(measure_vals)]
        self.is_fitted_ = True

        return self
