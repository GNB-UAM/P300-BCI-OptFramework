"""
This script will apply a regular pre-processing
over @won_eeg_2022 data, specifically:
· Common Average Referencing
· 4th order FW-BW Butterworth Filter 0.5-10Hz
· Epochs extraction [0, 600ms] relative to stimulus onset
· Baseline correction with 200ms before the stimulus onset
· Downsample from 512Hz to 20Hz by averaging 24-time points
without overlapping.

Please note that to make the preprocessing as similar to
@hoffmann_efficient_2008 as possible, we will consider
every word spelled as a session and every letter spelled
as a run. This will give us:
- 6 sessions per subject (2 of them with 5 runs, and 4
with 7 runs, however the number of runs will be made
homogeneous to always have 5 runs).

Also note that Hoffmann and Won share the same electrodes
setup (with the same indexes as well).

This script is based on the original preprocessing pipeline:
https://github.com/Kyungho-Won/EEG-dataset-for-RSVP-P300-speller/tree/main/Python

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 03/06/2025
"""

import os
import argparse
import numpy as np
import pickle as pkl
from tqdm import tqdm
from pathlib import Path
from mat73 import loadmat
from typing import List, Dict
from WonElect import (WonElect,
                      ELECT_SETS)
from scipy.signal import (butter,
                          sosfiltfilt)
from path_utils import get_run_path
from constants import (WON_SUBJECTS,
                       WON_SFREQ,
                       WON_TRIAL_EPOCHS,
                       WON_RUN_TRIALS,
                       WON_RUNS)


def bandpass_filter(
        X: np.ndarray, srate: int,
        lfreq: float, hfreq: float,
        order: int) -> np.ndarray:
    """
    Forward-Backward third order Butterworth
    bandpass filter between 1 & 12 Hz.

    :param X:The input signal matrix,
    expected shape: (n_feats, n_timesteps)
    :param srate: Time series sampling rate.
    :param lfreq: Band-pass low-frequency cut-off.
    :param hfreq: Band-pass high-frequency cut-off.
    :param order: Filter order.
    :return np.array: The filtered
    signal matrix.
    """
    nyq = srate/2
    Wn = [lfreq/nyq, hfreq/nyq]  # cutoff frequencies
    btype = 'bandpass'      # filter type (forward-backward Butterworth)
    output = 'sos'           # output format (second-order sections)

    # Create the filter object
    sos = butter(
        order, Wn,
        btype=btype,
        output=output
    )

    # Apply the filter to the signals
    X_filtered = sosfiltfilt(
        sos, X, axis=1)

    return X_filtered


def extract_epochs(
        data: np.ndarray, event: np.array,
        srate: int, baseline: List[int],
        frame: List[int], opt_keep_baseline: bool) -> np.ndarray:
    """
    This method will extract the epochs from raw EEG time
    series given a sequence of indexes (`events`)
    highlighting the beginning of each stimulus.

    Method adapted from:
    https://github.com/Kyungho-Won/EEG-dataset-for-RSVP-P300-speller/blob/main/Python/functions/func_preproc.py

    :param data: 2D data with shape: (n_electr, n_samples)
    :param event: 1D array with the stimulus onset indexes
    to extract.
    :param srate: Sampling frequency.
    :param baseline: List with beginning and end timesteps
    in miliseconds for the baseline computation.
    :param frame: List with beginning and end timesteps
    in miliseconds for the epoching step.
    :param opt_keep_baseline: Whether to keep or not the
    baseline interval.

    :return np.ndarray: A 3D array with shapes:
        (n_electr, n_timesteps, n_epochs)
    """
    n_electr = data.shape[0]

    # Memory pre-allocation
    if opt_keep_baseline is True:
        begin_tmp = int(np.floor(baseline[0]/1e3 * srate))
        end_tmp = int(begin_tmp + np.floor(
            frame[1]-baseline[0])/1e3 * srate)
    else:
        begin_tmp = int(np.floor(frame[0]/1e3 * srate))
        end_tmp = int(begin_tmp + np.floor(
            frame[1]-frame[0])/1e3 * srate)
    epoch3D = np.zeros(
        (n_electr, end_tmp-begin_tmp, len(event)))

    # Epoching
    nth_event = 0
    for i in event:
        if opt_keep_baseline is True:
            begin_id = int(i + np.floor(
                baseline[0]/1e3 * srate))
            end_id = int(
                begin_id + np.floor(
                    (frame[1]-baseline[0])/1e3 * srate))
        else:
            begin_id = int(i + np.floor(
                frame[0]/1e3 * srate))
            end_id = int(begin_id + np.floor(
                (frame[1]-frame[0])/1e3 * srate))

        # whole interval
        tmp_data = data[:, begin_id:end_id]

        # baseline interval
        begin_base = int(np.floor(baseline[0]/1e3 * srate))
        end_base = int(begin_base + np.floor(
            np.diff(baseline).squeeze()/1e3 * srate)-1)
        base = np.mean(
            tmp_data[:, begin_base:end_base], axis=1)

        # baselined data
        rmbase_data = tmp_data - base[:, np.newaxis]

        # storing baselined data
        epoch3D[:, :, nth_event] = rmbase_data
        nth_event = nth_event + 1

    return epoch3D


def decimation_by_avg(
        data: np.ndarray,
        factor: int) -> np.ndarray:
    """
    This method will downsample the EEG time series from
    the extracted epochs by `factor`.

    This method was adapted from:
    https://github.com/Kyungho-Won/EEG-dataset-for-RSVP-P300-speller/blob/main/Python/functions/func_preproc.py

    :param data: 3D epochs with shape:
        (n_electr, n_timesteps, n_epochs)
    :param factor: Decimation factor.

    :return np.ndarray: 3D decimated epochs with shape:
        (n_electr, np.floor(n_timesteps/factor), n_epochs)
    """
    ratio_dsample = factor
    n_electr, n_timesteps, n_epochs = data.shape

    # memory pre-allocation
    decimated_frame = int(np.floor(
        n_timesteps/ratio_dsample))
    decimated_data = np.zeros(
        (n_electr, decimated_frame, n_epochs))

    # average point decimation
    for i in range(n_epochs):
        for j in range(decimated_frame):
            cur_data = data[:, :, i]
            decimated_data[:, j, i] = np.mean(
                cur_data[:, j*ratio_dsample:(j+1)*ratio_dsample], axis=1)

    return decimated_data


def preproc_data(
        data: np.ndarray,
        seqs: np.array,
        subject_nr: int,
        elect_set: Dict[int, List[WonElect]],
        desired_sfreq: int,
        n_runs: int,
        window_len: float = 0.6) -> np.array:
    '''
    This method will preprocess all data following
    @won_eeg_2022.

    :param data: 2D array with shape:
        (n_electr, n_samples)
    :param seqs: 1D array with the stimuli IDs with shape:
        (n_samples,)
    :param subject_nr: Subject identifier.
    :param elect_set: Chosen electrodes' set.
    :param desired_sfreq: Desired sample's frequency
    after downsampling.
    :param n_runs: Number of runs.
    :param window_len: Epoch's length in seconds,
    defaults to 0.6.

    :return np.array: Array with all the
    data, dimensions:
        (n_electr, n_runs, n_trials, 12 epochs, timesteps)
    '''
    # Choose electrodes
    X_sess = data[elect_set[subject_nr]]

    # Referencing
    X_sess = X_sess - X_sess.mean(axis=1)[:, np.newaxis]

    # Band-pass filtering
    X_sess = bandpass_filter(
        X_sess, WON_SFREQ,
        lfreq=0.5, hfreq=10,
        order=4
    )

    # Epoching
    X_sess = extract_epochs(
        X_sess, np.argwhere(seqs != 0).flatten(),
        srate=WON_SFREQ,
        baseline=(-200, 0),
        frame=(0, window_len * 1e3),
        opt_keep_baseline=False
    )

    # Down-sampling
    X_sess = decimation_by_avg(
        X_sess, WON_SFREQ//desired_sfreq)

    # Swap to have (n_electr, n_epochs, n_timesteps)
    X_sess = X_sess.swapaxes(1, 2)

    # Reshape into (n_electr, n_runs, n_trials, 12, n_timesteps)
    X_sess = X_sess.reshape((
        X_sess.shape[0], n_runs,
        X_sess.shape[1]//WON_TRIAL_EPOCHS//n_runs,
        WON_TRIAL_EPOCHS, X_sess.shape[2]
    ))

    return X_sess


parser = argparse.ArgumentParser()

parser.add_argument(
    "-s", "--subject", type=int,
    help="Id of the subject to be processed",
    required=True, dest="subject_nr",
    choices=WON_SUBJECTS
)

parser.add_argument(
    "-id", "--input-dir-path", type=str,
    help="Path to the directory containing the data",
    required=True, dest="in_dir_path"
)

parser.add_argument(
    "-od", "--output-dir-path", type=str,
    help="Path to the directory containing the epoched",
    required=True, dest="out_dir_path"
)

parser.add_argument(
    "-el", "--epoch-length", type=float,
    help="Epoch's length in seconds",
    required=False, dest="epoch_len",
    default=.6
)

parser.add_argument(
    "-sfreq", "--sampling-frequency", type=int,
    help="Desired sampling frequency after downsampling",
    required=False, dest="sfreq",
    default=20
)

group_feat = parser.add_argument_group("Features options")
group_feat.add_argument(
    "-es", "--electrode-set", type=str,
    help="This argument will specify the electrode set" +
    "to employ",
    choices=list(ELECT_SETS.keys()), required=True,
    dest="elect_set"
)
group_feat.add_argument(
    "-cs", "--custom-set", type=int, nargs="+",
    help="This argument will specify a custom electrode set" +
    "to employ, this program expects indexes, have a look at" +
    "`WonElect`'s enumeration for more information",
    required=False, dest="custom_set", default=list()
)

# EXAMPLE = [
#     "-s", "1", "-id",
#     "data/won_eeg_2022/OriginalDataWon",
#     "-od", "preproc/won",
#     "-el", ".6",
#     "-sfreq", "20",
#     "-es", "All"
# ]

if __name__ == "__main__":
    args = parser.parse_args()
    in_dir = Path(args.in_dir_path)

    elect_set = {
        sbj: args.custom_set for sbj in WON_SUBJECTS
    } if args.elect_set == "Custom" else ELECT_SETS[
        args.elect_set]

    # Load all data
    data = loadmat(
        in_dir / "subject{}/s{:02d}.mat".format(
            args.subject_nr, args.subject_nr),
        use_attrdict=True
    )

    session_nr = 1
    sessions = data["train"] + data["test"]
    for sess in tqdm(sessions):
        X_sess = sess["data"]
        seqs = sess["markers_seq"]
        tgts = sess["markers_target"]
        # As many runs as characters to spell
        n_runs = len(sess["text_to_spell"])

        # Data's preprocessing
        X_sess = preproc_data(
            X_sess, seqs, args.subject_nr,
            elect_set, args.sfreq, n_runs,
            args.epoch_len
        )

        # Stimulus Sequences' extraction
        stim_seq = seqs[seqs != 0].astype(int) - 1  # Begins at 1
        y_sess = tgts[tgts != 0].astype(int) - 1  # Begins at 1
        # Transform zeroes into ones and viceversa
        # (to make targets be "1")
        y_sess = (y_sess == 0).astype(int)

        # Reshape from (n_epochs,) into (n_runs, n_trials, 12)
        stim_seq = stim_seq.reshape(
            n_runs,
            len(stim_seq)//WON_TRIAL_EPOCHS//n_runs,
            WON_TRIAL_EPOCHS
        )
        y_sess = y_sess.reshape(
            n_runs,
            len(y_sess)//WON_TRIAL_EPOCHS//n_runs,
            WON_TRIAL_EPOCHS
        )

        # Get run targets
        stim_tgt = stim_seq.flatten()[
            y_sess.flatten() == 1
        ].reshape(n_runs, WON_RUN_TRIALS, 2)  # 2 since there are two targets
        stim_tgt.sort()  # Rows first, Columns after
        stim_tgt = stim_tgt[:, 0]  # Since they will be repeated per trial

        # Save epoched data by run (fixed to just WON_RUNS
        # to make arrays homogeneous)
        for run_nr in WON_RUNS:
            # -1 because it is not an index
            X_run = X_sess[:, run_nr - 1]
            y_run = y_sess[run_nr - 1]
            stim_seq_run = stim_seq[run_nr - 1]
            stim_tgt_run = stim_tgt[run_nr - 1]

            out_path = get_run_path(
                args.out_dir_path, args.subject_nr,
                session_nr, run_nr, empty_dir=True
            )

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'wb') as f:
                pkl.dump((X_run, y_run, stim_seq_run, stim_tgt_run), f)

        session_nr += 1

    # Add metadata
    subject_dir_path = Path(
        args.out_dir_path) / f"subject{args.subject_nr}"

    elect_idxs = elect_set[args.subject_nr]
    elect_names = np.array(list(WonElect.__members__))
    with open(subject_dir_path / "electrodes.pkl", "wb") as f:
        pkl.dump(elect_names[elect_idxs], f)
