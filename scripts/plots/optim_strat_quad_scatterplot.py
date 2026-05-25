'''
This script will represent results for all possible
combinations of Datasets-ERP Detectors-Optimisation
Strategies (the Early Stop Strategy will be fixed).

They'll be represented within a 2D-Scatter Plot
(mean +/- std).

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 29/07/2025
'''
import argparse
import numpy as np
import pandas as pd
from plots import save_plot
import matplotlib.pyplot as plt
from constants import (DATASETS,
                       FONT_SIZE,
                       COLORS_OS)
from early_stop import (FixedStop,
                        AccumEvid,
                        StatsTest)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from sklearn.metrics import r2_score
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

plt.rcParams.update({
    'font.size': FONT_SIZE/1.5,
    'font.family': 'Times New Roman'
})

DS = DATASETS.keys()

ESS_HATCHES = {
    FixedStop.__name__: '///',
    AccumEvid.__name__: '**',
    StatsTest.__name__: '..'
}

ERPD_LABELS = {
    LinearDiscriminantAnalysis.__name__: "BLDA",
    RandomForestClassifier.__name__: "RandomForest",
    SVC.__name__: "SVC",
    LinearSVC.__name__: "LinearSVC"
}
ERPD_MARKERS = {
    LinearDiscriminantAnalysis.__name__: 's',
    RandomForestClassifier.__name__: 'p',
    SVC.__name__: 'o',
    LinearSVC.__name__: 'o'
}


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
    help="Path in which the plot will be stored",
    required=True, dest="out_path"
)

parser_strat = parser.add_argument_group(
    "Strategy options")
parser_strat.add_argument(
    "-ess", "--early-stop",
    choices=ESS_HATCHES.keys(),
    nargs='+',
    help="Early stop strategy to fix",
    required=True, dest="ess"
)
parser_strat.add_argument(
    "-erpd", "--erp-detector",
    choices=ERPD_LABELS.keys(),
    nargs='+',
    help="ERP detector to fix",
    required=True, dest="erpd"
)
parser_strat.add_argument(
    "-ds", "--dataset",
    choices=DS,
    help="Dataset to fix",
    required=True, dest="ds"
)

parser_plot = parser.add_argument_group(
    "Plot options")
parser_plot.add_argument(
    "-s", "--samples",
    help="Whether to also include samples or not",
    action="store_true",
    dest="plot_samples",
    default=False
)
parser_plot.add_argument(
    "-oslcr", "--os-legend-center-right",
    help="Whether to center the optimization strategies " +
    "legend to the right or not",
    action="store_true",
    dest="oslcr",
    default=False
)
parser_plot.add_argument(
    "-ac", "--adjust-curve",
    help="Whether to adjust a curve and plot it on the results or not.",
    action="store_true",
    dest="ac",
    default=False
)

if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()

    # Load & Fix ESS
    df = pd.read_csv(args.in_path, index_col=0).dropna()
    df = df[(df["ESS"].isin(args.ess)) &
            (df["ERPd"].isin(args.erpd)) &
            (df["Dataset"] == args.ds)]

    # Plots
    suptitle = f"{args.ds} — Trial-score mean"
    suptitle_erpd = ""

    fig, ax = plt.subplots(figsize=(7, 5))
    optim_strats = ["ITR", "¾Gain + ¼Cons",
                    "½Gain + ½Cons", "¼Gain + ¾Cons"]
    args.erpd = args.erpd
    args.ess = args.ess

    if args.ac:
        cols = ["Strategy", "ESS", "ERPd",
                "ObtainedAcc", "RequiredTrials"]

        XY = df[cols].groupby(
            ["Strategy", "ESS", "ERPd"]).mean()[
            ["ObtainedAcc", "RequiredTrials"]
        ].to_numpy()
        x, y = XY[:, 0], XY[:, 1]

        p = np.poly1d(np.polyfit(x, y, deg=1))
        ox = np.linspace(0, 1, num=100)
        ax.plot(ox, p(ox), linestyle="--", color="purple")

        y_pred = p(x)
        r2 = r2_score(y, y_pred)
        ax.text(0.8, 0.5, f"R² score: {r2:.4f}", color="purple")

    for idx_os, os in enumerate(optim_strats):
        df_os = df[df["Strategy"] == os]

        # TODO: Remove this plot
        #
        # ax.scatter(
        #     df_os["ObtainedAcc"].mean(),
        #     df_os["RequiredTrials"].mean(),
        #     c=COLORS_OS[idx_os],
        #     s=200,
        #     marker='x',
        # )
        # ax.errorbar(
        #     df_os["ObtainedAcc"].mean(),
        #     df_os["RequiredTrials"].mean(),
        #     xerr=df_os["ObtainedAcc"].std(),
        #     yerr=df_os["RequiredTrials"].std(),
        #     color=COLORS_OS[idx_os],
        #     markersize=7, label=os,
        #     capsize=5, linewidth=2,
        #     alpha=.4
        # )

        # Plot average for every ERPd + ESS combination
        if args.plot_samples:
            for idx_erpd, erpd in enumerate(args.erpd):
                for idx_ess, ess in enumerate(args.ess):
                    df_filt = df[(df["Strategy"] == os) &
                                 (df["ERPd"] == erpd) &
                                 (df["ESS"] == ess)]

                    ax.scatter(
                        df_filt["ObtainedAcc"].mean(),
                        df_filt["RequiredTrials"].mean(),
                        c=COLORS_OS[idx_os],
                        s=300,
                        marker=ERPD_MARKERS[erpd],
                        hatch=ESS_HATCHES[ess],
                        alpha=.7
                    )

    # Quadrants' settings
    fontsize = 48
    color = "#F6B80865"
    plt.text(0.25, 0.75, "Q41", fontsize=fontsize,
             color=color, ha="center",
             va="center", transform=ax.transAxes,
             alpha=.4)
    plt.text(0.75, 0.75, "Q42", fontsize=fontsize,
             color=color, ha="center",
             va="center", transform=ax.transAxes,
             alpha=.4)
    plt.text(0.25, 0.25, "Q43", fontsize=fontsize,
             color=color, ha="center",
             va="center", transform=ax.transAxes,
             alpha=.4)
    plt.text(0.75, 0.25, "Q44", fontsize=fontsize,
             color=color, ha="center",
             va="center", transform=ax.transAxes,
             alpha=.4)

    plt.hlines(5, 0.5, 1, colors=color,
               linestyles="--", linewidth=4,
               alpha=.4)
    plt.vlines(0.75, 0, 10, colors=color,
               linestyles="--", linewidth=4,
               alpha=.4)

    # First legend
    handles = [
        Line2D([0], [0], color=c, linewidth=4)
        for c in COLORS_OS
    ]
    leg1 = ax.legend(
        loc="center right" if args.oslcr else "center left",
        handles=handles, framealpha=.4,
        labels=optim_strats, prop={"size": 12},
        title="Optimization strategy",
        title_fontsize=14, ncol=1
    )
    ax.add_artist(leg1)

    # Additional legends
    if args.plot_samples:
        if len(args.erpd) > 1:
            # Second legend
            handles = [
                Line2D([0], [0], color="black",
                       marker=ERPD_MARKERS[erpd],
                       markerfacecolor="white", markersize=10,
                       linestyle="None")
                for erpd in args.erpd
            ]
            leg2 = plt.legend(
                loc="lower center", handles=handles, framealpha=.4,
                labels=list(map(lambda x: ERPD_LABELS[x], args.erpd)),
                prop={"size": 12}, title="Classifier", title_fontsize=14,
                ncol=len(args.erpd)
            )
            ax.add_artist(leg2)
        else:
            # Add just a suptitle in case we only have a single ERPd
            suptitle_erpd = f" ({ERPD_LABELS[args.erpd[0]]})"

        # Third legend
        handles = [
            Patch(edgecolor="black", facecolor="white",
                  hatch=ESS_HATCHES[ess])
            for ess in args.ess
        ]
        leg3 = plt.legend(
            loc="upper center", handles=handles, framealpha=.4,
            labels=list(args.ess), prop={"size": 12},
            title="Early stop", title_fontsize=14, ncol=len(args.ess)
        )

    ax.set_title(suptitle + suptitle_erpd)
    ax.set_ylim(0, 10)
    ax.set_xlim(0.5, 1)
    ax.set_xlabel("Obtained accuracy")
    ax.set_ylabel("Required trials")
    ax.grid()

    fig.tight_layout()
    save_plot(args.out_path)
