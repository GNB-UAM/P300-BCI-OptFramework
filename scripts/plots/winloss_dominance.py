"""
This script will plot within a stacked barplot
the proportion of win-tie-loss of an optimization
strategy against another.
- When accuracy mode is specified, higher is better.
- When trial mode is specified, lower is better.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 10/03/2026
"""

import os
import argparse
import pandas as pd
from pathlib import Path
from plots import save_plot
import matplotlib.pyplot as plt
from dist_utils import DistMode
import matplotlib.ticker as mtick
from itertools import combinations
from constants import FONT_SIZE, FRACTION_TO_ALPHA

KEEP_COLS = ["Dataset", "ES", "ERPd", "ESS", "Strategy",
             "Subject", "SessionOut", "ObtainedAcc",
             "RequiredTrials"]

plt.rcParams.update({
    'font.size': FONT_SIZE/1.5,
    'font.family': 'Times New Roman'
})

parser = argparse.ArgumentParser()

parser_io = parser.add_argument_group("I/O settings")
parser_io.add_argument(
    "-i", "--input", type=str,
    help="Path to the file containing the results",
    required=True, dest="in_path"
)
parser_io.add_argument(
    "-o", "--output", type=str,
    help="Path in which we'll save the figure",
    required=True, dest="out_path"
)

parser_opt = parser.add_argument_group(
    "Main options")
parser_opt.add_argument(
    "-m", "--mode", type=DistMode,
    choices=list(DistMode),
    help="Consider either trials or accuracy.",
    required=True, dest="mode"
)
parser_opt.add_argument(
    "-s", "--strat", type=str,
    help="Strategy to evaluate against the rest.",
    required=True, dest="strat"
)


def get_win_tie_loss(
        data: pd.DataFrame,
        mode: str) -> pd.DataFrame:
    strategies = df.index.unique("Strategy")
    wins = pd.DataFrame(0, index=strategies, columns=strategies)
    ties = pd.DataFrame(0, index=strategies, columns=strategies)

    group_levels = ["Dataset", "ES", "ERPd", "ESS",
                    "Subject", "SessionOut"]

    for _, g in df.groupby(level=group_levels):
        g = g.reset_index("Strategy")
        for s1, s2 in combinations(g["Strategy"], 2):

            val1 = g.loc[g["Strategy"] == s1, mode].values[0]
            val2 = g.loc[g["Strategy"] == s2, mode].values[0]

            if mode == "ObtainedAcc":
                if val1 > val2:
                    wins.loc[s1, s2] += 1
                elif val2 > val1:
                    wins.loc[s2, s1] += 1
                else:
                    ties.loc[s1, s2] += 1
                    ties.loc[s2, s1] += 1
            elif mode == "RequiredTrials":
                if val1 < val2:
                    wins.loc[s1, s2] += 1
                elif val2 < val1:
                    wins.loc[s2, s1] += 1
                else:
                    ties.loc[s1, s2] += 1
                    ties.loc[s2, s1] += 1

    total = wins + wins.T + ties
    wins_ratio = wins / total
    ties_ratio = ties / total

    return pd.concat({
        "Win": wins_ratio.stack(),
        "Tie": ties_ratio.stack(),
        "Loss": (wins.T / total).stack()
    }, axis=1).rename_axis(["Strategy_A", "Strategy_B"]).reset_index()


def draw_stacked_barplot(df_wtl: pd.DataFrame, strat: str, mode: str):

    title = f"{FRACTION_TO_ALPHA[strat]} versus rest " +\
        f"({'Speed' if mode == 'RequiredTrials' else 'Accuracy'})"

    df_wtl_filt = df_wtl[df_wtl["Strategy_A"] == strat]
    plot_data = df_wtl_filt.set_index("Strategy_B")[["Win", "Tie", "Loss"]]

    # nicer colors
    colors = {
        "Win": "#4CAF50",   # green
        "Tie": "#9E9E9E",   # gray
        "Loss": "#E53935"   # red
    }

    fig, ax = plt.subplots(figsize=(6, 7))
    bottom = None
    for outcome in ["Win", "Tie", "Loss"]:
        ax.bar(
            plot_data.index,
            plot_data[outcome],
            bottom=bottom,
            color=colors[outcome],
            label=outcome,
            width=0.65,
            edgecolor="black",
            linewidth=0.5
        )
        bottom = plot_data[outcome] if bottom is None else bottom + \
            plot_data[outcome]

    # formatting
    ax.set_title(title)
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Comparison")

    ax.set_ylim(0, 1)

    ax.set_xticklabels(
        [f"{FRACTION_TO_ALPHA[s]}" for s in plot_data.index], rotation=25)

    # percentage y-axis
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # clean look
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(title="Outcome")
    plt.tight_layout()


if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()

    if args.mode == DistMode.ObtainedAcc:
        mode = "ObtainedAcc"
    elif args.mode == DistMode.RequiredTri:
        mode = "RequiredTrials"
    else:
        raise Exception(f"Invalid mode provided: {args.mode}\n" +
                        f"Available: {list(DistMode)}")

    # Load results
    df = pd.read_csv(args.in_path, usecols=KEEP_COLS)
    # prepare indexes
    df = df.set_index(["Dataset", "ES", "ERPd", "ESS",
                       "Strategy", "Subject", "SessionOut"])

    # Output dir
    out_path = Path(args.out_path)
    os.makedirs(os.path.dirname(
        out_path), exist_ok=True)

    # Win-Tie-Loss dataframe
    df_wtl = get_win_tie_loss(df, mode)
    draw_stacked_barplot(df_wtl, args.strat, mode)
    save_plot(args.out_path)
