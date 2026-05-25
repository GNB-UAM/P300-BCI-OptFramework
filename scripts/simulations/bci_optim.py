"""
This script will optimise the hyperparameters
of both transducer and control interface at
subject-level (first the transducer and then
the control interface).

The whole optimisation process will be encapsulated
withing a (k-1)-Cross Validation process and evaluated
on every session left-out.

The transducer will be optimised considering the PR-AUC
value (due to the imbalanced nature of P300-ERP datasets)
whereas the control interface will consider the chosen
optimisation strategy (ITR, ¾Gain + ¼Cons, ...).

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 12/01/2026
"""
import re
import time
import optuna
import logging
import argparse
import numpy as np
from metrics import (itr,
                     gcb,
                     bcim_gc)
from logs import cfg_logger
from constants import (DATASETS,
                       OPTIM_STRATEGIES)
from datetime import datetime
from functools import partial
from sklearn.svm import LinearSVC
from early_stop import (EarlyStop,
                        FixedStop,
                        AccumEvid,
                        StatsTest)
from data_utils import (load_data,
                        sklearn_reshape)
from split_utils import index_data
from collections import defaultdict
from typing import List, Dict, Tuple
from sklearn.base import TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve, auc
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

TIMEOUT = 180

ERPd = {
    LinearSVC.__name__: LinearSVC,
    RandomForestClassifier.__name__: RandomForestClassifier,
    LinearDiscriminantAnalysis.__name__: partial(
        LinearDiscriminantAnalysis, solver="lsqr"),
}
ERPd_HP = {
    LinearSVC.__name__: lambda trial: {
        "C": trial.suggest_float("C", 1e-3, 1),
    },
    RandomForestClassifier.__name__: lambda trial: {
        "n_estimators": trial.suggest_int(
            "n_estimators", 50, 305),
    },
    LinearDiscriminantAnalysis.__name__: lambda trial: {
        "shrinkage": trial.suggest_categorical("shrinkage", [
            "auto", None] + np.linspace(1e-3, 1, num=14).tolist())
    },
}
ERPd_GRID = {
    LinearSVC.__name__: {
        'C': np.linspace(start=1e-3, stop=1, num=16)},
    RandomForestClassifier.__name__: {
        "n_estimators": [int(x) for x in np.linspace(
            50, 305, num=16, dtype=int)]},
    LinearDiscriminantAnalysis.__name__: {
        "shrinkage": ["auto", None] + np.linspace(
            1e-3, 1, num=14).tolist()},
}

ESS = {
    FixedStop.__name__: FixedStop,
    AccumEvid.__name__: AccumEvid,
    StatsTest.__name__: StatsTest
}


parser = argparse.ArgumentParser()
parser_data = parser.add_argument_group(
    "Data options")
parser_data.add_argument(
    "-d", "--dataset", type=str,
    help="Dataset to process",
    choices=DATASETS.keys(),
    required=True, dest="dname"
)
parser_data.add_argument(
    "-s", "--subject", type=int,
    help="Subject to consider (1-4, 6-9 for " +
    "Hoffmann and 1-55 for Won)",
    required=True, dest="subject_nr"
)

parser_io = parser.add_argument_group(
    "I/O options")
parser_io.add_argument(
    "-id", "--input-dir-path", type=str,
    help="Path to the directory containing data",
    required=True, dest="in_dir_path"
)
parser_io.add_argument(
    "-o", "--output", type=str,
    help="Relational DataBase name",
    required=True, dest="rdbname"
)

parser_strat = parser.add_argument_group(
    "Strategy options")
parser_strat.add_argument(
    "-os", "--optim-strat", nargs='+',
    help="Optimisation strategies to evaluate " +
    "(either a float in [0, 1] or a string " +
    f"from {OPTIM_STRATEGIES.keys()})",
    required=True, dest="os_strats"
)
parser_strat.add_argument(
    "-std", "--standard-scaler",
    help="Whether to apply or not a StandardScaler " +
    "before showing samples to the ERP detector.",
    action="store_true", default=False, dest="std"
)
parser_strat.add_argument(
    "-erpd", "--erp-detector",
    choices=ERPd.keys(),
    help="ERP detector to employ",
    required=True, dest="erpd"
)

parser_study = parser.add_argument_group(
    "Study options")
parser_study.add_argument(
    "-j", "--jobs", type=int,
    help="Number of study-trials to execute at once.",
    required=False, default=1,
    dest="n_jobs"
)
parser_study.add_argument(
    "-t", "--trials", type=int,
    help="Number of study-trials to execute.",
    required=False, default=16,
    dest="study_trials"
)

parser_log = parser.add_argument_group(
    "Logging options")
parser_log.add_argument(
    "-jctl", "--journalctl",
    help="If specified logs will be sent to journalctl, otherwise to stdout",
    action="store_true", default=False, dest="journalctl"
)


def parse_optim_strats(
        os_strats: List[str]) -> Dict[str, callable]:
    '''
    This method will interpret user args
    to execute different optimisation
    strategies.

    :param os_strats: List of optimisation
    strategies' names.

    :return Dict[str, callable]: A dictionary
    with every strategy name as key and its
    prepared measure function as value.
    '''
    strats_dict = {}

    for os in os_strats:
        if os == "ITR":
            strats_dict[os] = partial(
                bcim_gc, measure=itr,
                n_classes=n_flashes,
                trial_secs=trial_secs
            )
        elif re.match(r".*Gain \+ .*Cons", os):
            strats_dict[os] = partial(
                gcb, weights=OPTIM_STRATEGIES[os])
        else:
            alpha = float(os)
            os_name = f"{alpha:.3f}Gain + {(1-alpha):.3f}Cons"
            strats_dict[os_name] = partial(gcb, weights=(alpha, 1-alpha))

    return strats_dict


def objective(
        trial: optuna.Trial,
        X: np.ndarray,
        y: np.ndarray,
        stim_seq: np.ndarray,
        stim_tgt: np.ndarray,
        runs_ids: np.array,
        std: bool,
        erpd: TransformerMixin,
        erpd_hp: callable,
        needs_cal: bool,
        logger_time: logging.Logger) -> float:
    '''
    CV-objective function to optimize with Optuna.

    :param trial: Optuna's trial.
    :param X: CV-data with shape: (n_runs, n_epochs, n_features)
    :param y: CV-labels with shape: (n_runs, n_epochs)
    :param stim_seq: CV-stimulus sequence with shape: (n_runs, n_epochs)
    :param stim_tgt: CV-stimulus targets with shape: (n_runs, n_it)
    :param runs_ids: CV-runs ids with shape: (n_runs,)
    :param std: Boolean indicating whether to apply standardization or not.
    :param erpd: ERP detector to fit and predict.
    :param erpd_hp: ERP detector hyperparameters to evaluate.
    :param needs_cal: Whether the current ERP detector needs to be calibrated
    or not.
    :param logger_time: Log to report time spent.
    '''

    folds, sessions_cv, erpd_params = list(), list(), list()
    evid_cv, stim_seq_cv, stim_tgt_cv = list(), list(), list()
    prauc_vals = list()

    logo = LeaveOneGroupOut()
    cvtime = time.time()
    for fold, (train_cv_idx, valid_cv_idx) in enumerate(logo.split(
            X, groups=runs_ids)):
        folds.append(fold)
        sessions_cv.append(int(runs_ids[valid_cv_idx][0]))

        # Train-Valid-Split
        X_train_cv, y_train_cv, stim_seq_train_cv, stim_tgt_train_cv =\
            index_data(train_cv_idx, X, y, stim_seq, stim_tgt)
        X_valid_cv, y_valid_cv, stim_seq_valid_cv, stim_tgt_valid_cv =\
            index_data(valid_cv_idx, X, y, stim_seq, stim_tgt)

        clftime = time.time()
        # Transducer training
        cv_erpd_params = erpd_hp(trial)
        erpd_params.append(cv_erpd_params)

        clf = erpd(**cv_erpd_params)
        clf_name = clf.__class__.__name__
        X_train_cv, y_train_cv = sklearn_reshape(
            X_train_cv, y_train_cv)
        if needs_cal:
            clf = CalibratedClassifierCV(estimator=clf)
        if std:
            scaler = StandardScaler()
            X_train_cv = scaler.fit_transform(X_train_cv)
        clf.fit(X_train_cv, y_train_cv)
        logger_time.info(
            f"{clf_name} " +
            f"training: {time.time() - clftime} (Fold {fold})"
        )

        evltime = time.time()
        # Transducer evaluation
        X_valid_cv, y_valid_cv = sklearn_reshape(
            X_valid_cv, y_valid_cv)
        if std:
            X_valid_cv = scaler.transform(X_valid_cv)
        y_pred_cv_proba = clf.predict_proba(X_valid_cv)[:, 1]

        logger_time.info(
            f"{clf_name} " +
            f"evaluation time: {time.time() - evltime} (Fold {fold})"
        )

        # CV process timeout
        if (time.time() - cvtime) >= TIMEOUT*2:
            raise optuna.TrialPruned()

        # Save results
        precision, recall, _ = precision_recall_curve(
            y_valid_cv, y_pred_cv_proba)
        prauc_vals.append(auc(recall, precision))
        evid_cv.append(y_pred_cv_proba)
        stim_seq_cv.append(stim_seq_valid_cv)
        stim_tgt_cv.append(stim_tgt_valid_cv)

    # User attributes
    trial.set_user_attr("CV_Session out", sessions_cv)
    trial.set_user_attr("CV_Folds", folds)
    trial.set_user_attr("CV_ERPd_HP", erpd_params)
    trial.set_user_attr("CV_PRAUC", prauc_vals)

    # data to adjust control-interfaces
    trial.set_user_attr(
        "CV_Evid", np.concatenate(evid_cv).tolist())
    trial.set_user_attr(
        "CV_StimSeq", np.concatenate(stim_seq_cv, axis=0).tolist())
    trial.set_user_attr(
        "CV_StimTgt", np.concatenate(stim_tgt_cv, axis=0).tolist())

    return np.mean(prauc_vals)


def optimise_ci(ess: EarlyStop, bline: EarlyStop,
                optim_strat: Tuple[str, callable],
                X_train: np.ndarray, X_test: np.ndarray,
                y_train: np.ndarray, y_test: np.ndarray,
                z_train: np.ndarray, z_test: np.ndarray,
                results: Dict[str, list]) -> Tuple[float, float]:
    """
    Optimise and track Control-Interface results.

    :param ess: Early Stop Strategy to test.
    :param optim_strat: Control-Interface optimisation
    strategy.
    :param X_train: Training evidences.
    :param y_train: Training stimulus sequences.
    :param z_train: Training target stimuli.
    :param X_train: Testing evidences.
    :param y_train: Testing stimulus sequences.
    :param z_train: Testing target stimuli.
    :param results: Dictionary with `list` as
    default value.

    :return Tuple[float, float]: Trials required and
    accuracy obtained on test, respectively.
    """

    os_name, os = optim_strat

    # Adjust Control-Interface
    ci.fit(X_train, y_train, z_train, bline, os)

    # Test Control-Interface
    gain_bci, t_base, t_req = EarlyStop.gain(
        bline, ci, X_test, y_test, return_extra=True)
    cons_bci, acc_base, acc_obtn = EarlyStop.cons(
        bline, ci, X_test, y_test, z_test, return_extra=True)

    # Save results
    os_results[os_name]["Test_OS"].append(os(
        gain_bci, cons_bci, t_base=t_base, acc_base=acc_base))
    os_results[os_name]["Test_Gain"].append(gain_bci)
    os_results[os_name]["Test_Cons"].append(cons_bci)

    os_results[os_name]["Test_BaselineTrials"].append(t_base)
    os_results[os_name]["Test_TrialsRequired"].append(t_req)

    os_results[os_name]["Test_BaselineAccuracy"].append(acc_base)
    os_results[os_name]["Test_ObtainedAccuracy"].append(acc_obtn)
    os_results[os_name]["Test_ESS_HP"].append(ci.get_params())

    return t_req, acc_obtn


if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()
    storage = optuna.storages.RDBStorage(
        f"sqlite:///{args.rdbname}.db",
        engine_kwargs={"connect_args": {"timeout": TIMEOUT}}
    )

    # logging
    logger = cfg_logger(
        optuna.logging.get_logger("optuna"), args.journalctl)
    logger_time = cfg_logger(
        logging.getLogger("optuna_time"), args.journalctl)

    # this flag is set to provide `LinearSVC` with `predict_proba`
    needs_cal = (args.erpd == LinearSVC.__name__)

    # dataset attributes
    mode = DATASETS[args.dname]["ess_mode"]
    tmax = DATASETS[args.dname]["n_trials"]
    n_flashes = DATASETS[args.dname]["n_stimulus"]
    trial_secs = DATASETS[args.dname]["trial_secs"]
    erpd_name = args.erpd + "Std" if args.std else args.erpd

    # parse optim strategies
    os_strats = parse_optim_strats(args.os_strats)

    # Load data & reshape
    X, y, stim_seq, stim_tgt, old_shape = load_data(
        args.in_dir_path, args.subject_nr)
    runs_ids = DATASETS[args.dname]["runs_ids"]
    n_electr = old_shape[1]

    for session_out in DATASETS[args.dname]["sessions"]:
        # -1 because it is not an index
        session_out -= 1

        # Leave-One-Session-Out (LOSSO)
        X_train, y_train, stim_seq_train, stim_tgt_train, runs_ids_train =\
            index_data(runs_ids != session_out,
                       X, y, stim_seq, stim_tgt, runs_ids)
        X_test, y_test, stim_seq_test, stim_tgt_test, runs_ids_test =\
            index_data(runs_ids == session_out,
                       X, y, stim_seq, stim_tgt, runs_ids)

        # Create Optuna-study
        date = datetime.now().strftime(
            "%Y-%m-%d_%H:%M:%S")
        study = optuna.create_study(
            study_name=f"{date}_{args.dname}_" +
            f"S{args.subject_nr}_LOSSO{session_out}_" +
            f"ERPd{erpd_name}",
            storage=storage,
            direction="maximize",
            sampler=optuna.samplers.GridSampler(
                ERPd_GRID[args.erpd]),
            load_if_exists=True
        )

        # user attributes
        study.set_user_attr("Dataset", args.dname)
        study.set_user_attr("Subject", args.subject_nr)
        study.set_user_attr("Session out", session_out)
        study.set_user_attr("ES", n_electr)
        study.set_user_attr("ERPd", args.erpd)

        # (k-1) cross-validation
        objective_cv = partial(
            objective, X=X_train, y=y_train,
            stim_seq=stim_seq_train,
            stim_tgt=stim_tgt_train,
            runs_ids=runs_ids_train,
            std=args.std,
            erpd=ERPd[args.erpd],
            erpd_hp=ERPd_HP[args.erpd],
            needs_cal=needs_cal,
            logger_time=logger_time
        )
        study.optimize(
            objective_cv,
            n_trials=args.study_trials,
            n_jobs=args.n_jobs
        )

        # Test LOSSO
        # best parameters
        erpd_params = study.best_trial.params
        evid_cv = np.asarray(study.best_trial.user_attrs["CV_Evid"])
        stim_seq_cv = np.asarray(study.best_trial.user_attrs["CV_StimSeq"])
        stim_tgt_cv = np.asarray(study.best_trial.user_attrs["CV_StimTgt"])

        # Adjust Transducer
        clf = ERPd[args.erpd](**erpd_params)
        clf_name = clf.__class__.__name__
        X_train, y_train = sklearn_reshape(
            X_train, y_train)
        if needs_cal:
            clf = CalibratedClassifierCV(estimator=clf)
        if args.std:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
        clf.fit(X_train, y_train)

        # Test Transducer
        X_test, y_test = sklearn_reshape(
            X_test, y_test)
        if args.std:
            X_test = scaler.transform(X_test)
        y_pred_proba = clf.predict_proba(X_test)[:, 1]

        precision, recall, _ = precision_recall_curve(
            y_test, y_pred_proba)
        test_score = auc(recall, precision)
        logger.info(f"Test {clf_name}: {test_score} PRAUC")

        # Optimise Control-Interfaces
        os_results = {}
        for os_name, os in os_strats.items():
            os_results[os_name] = defaultdict(list)
            for ess_name in ESS.keys():
                strat_bline = FixedStop(mode, n_flashes, tmax)
                ci = ESS[ess_name](mode=mode, n_flashes=n_flashes)

                t_req, acc_obtn = optimise_ci(
                    ci, strat_bline, (os_name, os),
                    X_train=evid_cv, X_test=y_pred_proba,
                    y_train=stim_seq_cv, y_test=stim_seq_test,
                    z_train=stim_tgt_cv, z_test=stim_tgt_test,
                    results=os_results
                )

                # Logs
                logger.info(f"Test {os_name}-{ess_name}: " +
                            f"{t_req} TR; {acc_obtn} OA")
                os_results[os_name]["Test_ESS"].append(ess_name)

        # User attributes
        study.set_user_attr("Test_PRAUC", test_score)
        study.set_user_attr("Test_ERPd_HP", erpd_params)
        study.set_user_attr("Test_CI", os_results)
