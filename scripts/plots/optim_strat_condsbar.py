'''
This script will plot expected accuracies or
trials for a series of fixed trials or accuracies
in the form of stacked bar-plots.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 21/01/2026
'''
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from plots import save_plot
from typing import Tuple, List
import matplotlib.pyplot as plt
from dist_utils import DistMode
from constants import (DATASETS,
                       COLORS_OS,
                       FONT_SIZE)
from sklearn.svm import LinearSVC
from early_stop import (FixedStop,
                        AccumEvid,
                        StatsTest)
from matplotlib.ticker import (Formatter,
                               FormatStrFormatter)
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

plt.rcParams.update({
    'font.size': FONT_SIZE/1.25,
    'font.family': 'Times New Roman',
    'svg.fonttype': 'none'
})

DS = DATASETS.keys()
DSET_ACC = {"Hoffmann": 6, "Won": 5, "WonRCP2RSVP": 10}
DSET_THR = {"Hoffmann": (0.1, 0.01), "Won": (0.1, 0.01),
            "WonRCP2RSVP": (0.1, 0.01)}

ESS = [
    FixedStop.__name__,
    AccumEvid.__name__,
    StatsTest.__name__
]
ERPd = [
    LinearSVC.__name__,
    RandomForestClassifier.__name__,
    LinearDiscriminantAnalysis.__name__
]

# Strategies
OPTIM_STRATS = [
    "ITR", "¾Gain + ¼Cons",
    "½Gain + ½Cons", "¼Gain + ¾Cons"
]

# Dataframe columns
DATA_COLS = ["ObtainedAcc", "RequiredTrials"]
COMM_COLS = ["ESS", "ERPd", "Dataset", "Strategy"] +\
    DATA_COLS

# Conditions to fix
COND_RANGE = {
    DistMode.ObtainedAcc: (0, 1),
    DistMode.RequiredTri: (1, 15)
}


def plot_stacked_barplot(X: np.array,
                         bins: np.array,
                         _range: Tuple[float, float],
                         threshold: float,
                         colors: List[str],
                         labels: List[str],
                         title: str,
                         xlabel: str,
                         formatter: Formatter,
                         ylim: Tuple[float, float] = (0, None)):

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 10))
    n, bins, patches = ax.hist(
        X, bins, density=True, color=colors,
        label=labels, stacked=True, range=_range
    )

    # Convert cumulative into actual segment heights
    n = np.array(n)
    heights = np.copy(n)

    heights[1:] = n[1:] - n[:-1]  # de-cumulate

    # Now label using the corrected heights
    for i, (h, patch_set) in enumerate(zip(heights, patches)):
        for height, rect in zip(h, patch_set):
            if height > threshold:
                x = rect.get_x() + rect.get_width() / 2
                y = rect.get_y() + rect.get_height() / 2

                ax.text(
                    x, y,
                    f"{height:.2f}",
                    ha='center', va='center',
                    fontsize=FONT_SIZE/1.5
                )

    # Other properties
    ax.set_xticks(bins, bins)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_ylim(*ylim)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Density")

    ax.legend()
    ax.grid()

    fig.tight_layout()


parser = argparse.ArgumentParser()

parser_io = parser.add_argument_group(
    "I/O options")
parser_io.add_argument(
    "-i", "--input", type=str,
    help="Path to CSV with data",
    required=True, dest="in_path"
)
parser_io.add_argument(
    "-o", "--output", type=str,
    help="Directory path in which the plot will be stored",
    required=True, dest="out_path"
)

parser_strat = parser.add_argument_group(
    "Strategy options")
parser_strat.add_argument(
    "-ess", "--early-stop",
    nargs="+",
    choices=ESS,
    help="Early stop strategy to fix",
    required=True, dest="ess"
)
parser_strat.add_argument(
    "-erpd", "--erp-detector",
    nargs="+",
    choices=ERPd,
    help="ERP detector to fix",
    required=True, dest="erpd"
)
parser_strat.add_argument(
    "-ds", "--dataset",
    choices=DS,
    help="Dataset to fix",
    required=True, dest="ds"
)

parser_his = parser.add_argument_group(
    "Population model options")
parser_his.add_argument(
    "-m", "--mode", type=DistMode,
    choices=list(DistMode),
    help="Condition distribution on the specified mode.",
    required=True, dest="mode"
)

parser_plot = parser.add_argument_group(
    "Plot settings")
parser_plot.add_argument(
    "-ylim", "--oy-limits", type=float,
    nargs=2, help="Limits of the OY axis",
    required=False, default=(0, None),
    dest="ylim"
)

if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()
    out_dir = Path(args.out_path)

    # OX-OY assignment
    if args.mode == DistMode.ObtainedAcc:
        cond = "ObtainedAcc"
        bins = np.linspace(0, 1, num=DSET_ACC[args.ds])
        threshold = DSET_THR[args.ds][0]
        formatter = FormatStrFormatter("%.2f")

        title = "Experiments density after fixing " +\
            f"accuracy — {args.ds}"
        xlabel = "Obtained accuracy"
    elif args.mode == DistMode.RequiredTri:
        cond = "RequiredTrials"
        bins = np.arange(1, 15+1)
        threshold = DSET_THR[args.ds][1]
        formatter = FormatStrFormatter("%d")

        title = "Experiments density after fixing " +\
            f"number of trials — {args.ds}"
        xlabel = "Required trials"
    else:
        raise Exception(f"Invalid mode provided: {args.mode}\n" +
                        f"Available: {list(DistMode)}")

    # Load & Filter
    df = pd.read_csv(args.in_path, index_col=0)[COMM_COLS]

    df = df[(df["ESS"].isin(args.ess)) &
            (df["ERPd"].isin(args.erpd)) &
            (df["Dataset"] == args.ds)][
        ["Strategy", "ObtainedAcc", "RequiredTrials"]]

    # Prepare data
    strats = ["ITR", "¾Gain + ¼Cons", "½Gain + ½Cons", "¼Gain + ¾Cons"]
    X = np.vstack([df[df["Strategy"] == s][cond] for s in strats]).T

    # Plot
    plot_stacked_barplot(
        X, bins=bins,
        _range=COND_RANGE[args.mode],
        threshold=threshold,
        colors=COLORS_OS,
        labels=strats,
        title=title,
        xlabel=xlabel,
        formatter=formatter,
        ylim=args.ylim
    )
    save_plot(out_dir / f"{args.mode.value}_condsbar.svg")
