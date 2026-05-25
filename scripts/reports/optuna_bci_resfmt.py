"""
This script will format the results obtained
with `bci_optim.py` to follow a common interface
all plot scripts need.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 13/01/2026
"""

import os
import optuna
import argparse
import pandas as pd
from tqdm import tqdm
from copy import copy
from typing import List, Dict, Any


def append_study(results: List[Dict[str, Any]],
                 study: optuna.Study) -> int:
    """
    This method will append all the necessary info
    from a specified trial to a given input list.

    :param results: Results with previous studies.
    :param study: Study to format.

    :return int: 0 if everything was OK, 1 if there
    is a failure.
    """
    study_attrs = study.user_attrs

    # Test failed
    if (study_attrs.get("Test_PRAUC") is None) or (
            study_attrs.get("Test_ERPd_HP") is None):
        return 1

    # Not list-type attributes
    base_dict = {
        "Dataset": study_attrs["Dataset"],
        "ERPd": study_attrs["ERPd"],
        "ES": study_attrs["ES"],
        "Session out": study_attrs["Session out"],
        "Subject": study_attrs["Subject"],
        "Test_ERPd_HP": study_attrs["Test_ERPd_HP"],
        "Test_PRAUC": study_attrs["Test_PRAUC"],
    }

    for key in base_dict:
        study_attrs.pop(key)

    # List-type attributes
    for os_name, os_vals in study_attrs["Test_CI"].items():
        os_dict = copy(base_dict)
        os_dict["OS"] = os_name

        for ess_idx in range(len(os_vals["Test_ESS"])):
            ess_dict = copy(os_dict)
            ess_dict.update({
                k: v[ess_idx] for k, v in
                os_vals.items()
            })

            results.append(ess_dict)

    return 0


def cols_rename(df: pd.DataFrame) -> pd.DataFrame:
    """
    This method will rename the original DataFrame
    to make it compatible with other scripts.

    :param df: Original report.

    :return pd.DataFrame: Renamed DataFrame.
    """
    df_new = df.rename(columns={
        # identifiers
        "Dataset": "Dataset",
        "ERPd": "ERPd",
        "ES": "ES",
        "OS": "Strategy",
        "Session out": "SessionOut",
        "Subject": "Subject",
        # measures
        "Test_BaselineAccuracy": "BaselineAcc",
        "Test_BaselineTrials": "BaselineTrials",
        "Test_Cons": "Cons",
        "Test_Gain": "Gain",
        "Test_OS": "StrategyVal",
        "Test_ObtainedAccuracy": "ObtainedAcc",
        "Test_TrialsRequired": "RequiredTrials",
        # other
        "Test_ERPd_HP": "ERPd_HP",
        "Test_ESS_HP": "ESS_HP",
        "Test_ESS": "ESS",
        "Test_PRAUC": "PRAUCScore",
    })

    return df_new


parser = argparse.ArgumentParser()
parser_io = parser.add_argument_group(
    "I/O options")
parser_io.add_argument(
    "-i", "--input", type=str, nargs='+',
    help="Path to Optuna's original reports",
    required=True, dest="in_path"
)
parser_io.add_argument(
    "-o", "--output", type=str,
    help="Path for the formatted report",
    required=True, dest="out_path"
)

if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()
    storages = [f"sqlite:///{path}" for path in args.in_path]

    fails = 0
    total = 0
    results = list()
    for storage in storages:
        print(f"Current study: {storage.split('/')[-1]}")
        for study_name in tqdm(optuna.get_all_study_names(storage)):
            study = optuna.load_study(
                study_name=study_name, storage=storage)
            fails += append_study(results, study)
            total += 1

    print(f"Number of failures: {fails}/{total}")

    # DataFrame
    df = pd.DataFrame(results)

    # rename and save
    df = cols_rename(df)

    parent = os.path.dirname(args.out_path)
    if parent != "":
        os.makedirs(parent, exist_ok=True)
    df.to_csv(args.out_path)
