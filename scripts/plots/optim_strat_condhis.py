'''
This script will plot expected accuracies or
trials for a series of fixed trials or accuracies
in the form of histograms, respectively.

All these results will be drawn from:
(being `f` a bidimensional histogram)
· f_Y|X>=x0 when fixing the accuracy.
· f_X|Y<=y0 when fixing the trial.

Note:
- "OA" stands for "Obtained Accuracies"
- "RT" stands for "Required Trials"

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 02/10/2025
'''
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from plots import save_plot
import matplotlib.pyplot as plt
from dist_utils import DistMode
from constants import (DATASETS,
                       COLORS_OS,
                       FONT_SIZE,
                       FRACTION_TO_ALPHA)
from sklearn.svm import LinearSVC
from early_stop import (FixedStop,
                        AccumEvid,
                        StatsTest)
from matplotlib.ticker import FormatStrFormatter
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

plt.rcParams.update({
    'font.size': FONT_SIZE/1.5,
    'font.family': 'Times New Roman',
    'svg.fonttype': 'none'
})
MARKRS_SIZE = 100

DS = DATASETS.keys()
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

# Space to consider (always with an extra
# sample to fill the whole figure!)
OALIMS = (0, 1)
RTLIMS = (1, 10)

# Strategies
OPTIM_STRATS = [
    "ITR", "¾Gain + ¼Cons",
    "½Gain + ½Cons", "¼Gain + ¾Cons"
]

# Dataframe columns
DATA_COLS = ["ObtainedAcc", "RequiredTrials"]
COMM_COLS = ["ESS", "ERPd", "Dataset", "Strategy"] +\
    DATA_COLS


def plot_fn(ax, x, y, label, color):
    width = x[1]-x[0]  # We assume uniform grid
    ax.bar(
        x, y, color=color, width=width,
        fill=True, linewidth=3,
        align="edge", label=label
    )


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
parser_his.add_argument(
    "-cnorm", "--common-norm",
    help="Whether to normalize by counting all " +
    "samples or by each strategy number of samples",
    action="store_true",
    dest="cnorm",
    default=False
)
parser_his.add_argument(
    "-bins", type=int, nargs=2,
    help="Histogram bins (Accuracy, Trials)",
    required=True, dest="bins"
)

parser_plot = parser.add_argument_group(
    "Plot settings")
parser_plot.add_argument(
    "-xlim", "--ox-limits", type=float,
    nargs=2, help="Limits of the OX axis",
    required=False, default=(None, None),
    dest="xlim"
)
parser_plot.add_argument(
    "-ylim", "--oy-limits", type=float,
    nargs=2, help="Limits of the OY axis",
    required=False, default=(None, None),
    dest="ylim"
)

if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()
    out_dir = Path(args.out_path)

    # OX-OY assignment
    if args.mode == DistMode.ObtainedAcc:
        oymode = DistMode.RequiredTri
        ge = True  # Greater or equal

        order = ["ObtainedAcc", "RequiredTrials"]
        hisrng = (OALIMS, RTLIMS)

        # Histogram's OA & RT bins, respectively
        bins = args.bins

        # Other
        formatter = FormatStrFormatter("%.2f")
        formatter_oy = FormatStrFormatter("%d")

        title = "Expected required trials after fixing accuracy (≥"
        xlabel = "Required trials"
    elif args.mode == DistMode.RequiredTri:
        oymode = DistMode.ObtainedAcc
        ge = False  # Greater or equal

        order = ["RequiredTrials", "ObtainedAcc"]
        hisrng = (RTLIMS, OALIMS)

        # Histogram's RT & OA bins, respectively
        bins = args.bins[::-1]

        # Other
        formatter = FormatStrFormatter("%d")
        formatter_oy = FormatStrFormatter("%.2f")

        title = "Expected accuracy after fixing trials (≤ "
        xlabel = "Accuracy"
    else:
        raise Exception(f"Invalid mode provided: {args.mode}\n" +
                        f"Available: {list(DistMode)}")

    # Load & Filter
    df = pd.read_csv(args.in_path, index_col=0)[COMM_COLS]
    df = df[(df["ESS"].isin(args.ess)) &
            (df["ERPd"].isin(args.erpd)) &
            (df["Dataset"] == args.ds)][
        ["Strategy", "ObtainedAcc", "RequiredTrials"]]

    # Obtain histograms per optimization strategy
    H = np.zeros((len(OPTIM_STRATS), *bins))
    xedges = np.zeros(bins[0] + 1)
    yedges = np.zeros(bins[1] + 1)
    for i, os in enumerate(OPTIM_STRATS):
        arr = df[df["Strategy"] == os][order].to_numpy().T
        # `xedges` and `yedges` will always be the same!
        H[i], xedges, yedges = np.histogram2d(
            *arr, bins=bins, range=hisrng, density=False)

    # Normalization (global VS strategy-level counts)
    if args.cnorm:
        H_norm = H/np.sum(H)
    else:
        H_norm = H/np.sum(H, axis=(
            1, 2), keepdims=True)

    # Conditioned plots
    conds = xedges[:-1]
    for x0_idx, x0 in tqdm(enumerate(conds)):
        fig, ax = plt.subplots(nrows=len(OPTIM_STRATS), figsize=(8, 12))
        for i, os in enumerate(OPTIM_STRATS):
            # H_cond = H_norm[i, x0_idx]
            if ge:
                H_cond = np.sum(H_norm[i, x0_idx:], axis=0)
            else:
                H_cond = np.sum(H_norm[i, :x0_idx+1], axis=0)

            plot_fn(ax[i], yedges[:-1], H_cond,
                    label=FRACTION_TO_ALPHA[os], color=COLORS_OS[i])

            if args.mode == DistMode.ObtainedAcc:
                ax[i].text(
                    0.41, 0.75,
                    transform=ax[i].transAxes,
                    s=f"Accumulated probability: {H_cond.sum():.3f}"
                )
            else:
                ax[i].text(
                    0.04, 0.75,
                    transform=ax[i].transAxes,
                    s=f"Accumulated probability: {H_cond.sum():.3f}"
                )

            # Plot settings
            ax[i].set_xlim(args.xlim)
            ax[i].set_ylim(args.ylim)
            ax[i].set_xlabel(xlabel)
            ax[i].set_ylabel("Probability")

            ax[i].set_xticks(yedges)
            ax[i].xaxis.set_major_formatter(formatter_oy)
            ax[i].tick_params(axis='x', labelrotation=45)

            if args.mode == DistMode.ObtainedAcc:
                ax[i].legend(loc="center right")
            else:
                ax[i].legend(loc="center left")

            ax[i].grid()

        fig.suptitle(title + formatter(x0) + ')')
        fig.tight_layout()
        save_plot(out_dir / f"{args.mode.value}_{x0:.2f}_condhis.svg")
