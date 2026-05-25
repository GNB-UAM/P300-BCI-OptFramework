'''
This script will plot a 2D histogram of the
trials required and obtained accuracies
for all the optimisation strategies.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 11/12/2025
'''

import os
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.cm as cm
from plots import save_plot
from matplotlib import ticker
from constants import FONT_SIZE
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Tuple, List, Dict
from scipy.stats import gaussian_kde

VIRIDIS_COLOR = "#440154"
STRATEGIES = ["ITR", "¾Gain + ¼Cons",
              "½Gain + ½Cons",
              "¼Gain + ¾Cons"]

plt.rcParams.update({
    'font.size': FONT_SIZE/1.5,
    'font.family': 'Times New Roman'
})


def gen_axes_layout(fig: plt.Figure,
                    strats: List[str]) -> Dict[str, plt.Axes]:
    mosaic = [[], []]
    for os_name in strats:
        fst_row = f"{os_name}_Px,{os_name}_Px,.,.".split(',')
        snd_row = f"{os_name}_Pxy,{os_name}_Pxy," +\
            f"{os_name}_Py,."
        snd_row = snd_row.split(',')

        mosaic[0].extend(fst_row)
        mosaic[1].extend(snd_row)
    mosaic[0].append(".")
    mosaic[1].append("Cbar")

    ax_dict = fig.subplot_mosaic(
        mosaic,
        height_ratios=[.125, .875],
        width_ratios=[.5, .5, .15, .1] * 4 + [.1],
        gridspec_kw={
            "wspace": 0,
            "hspace": 0,
        },
    )

    return ax_dict


def plot_Px(ax: plt.Axes,
            data_ox: np.array,
            title: str,
            xlim: Tuple[float],
            bins: int = 10,
            granularity: int = 100,
            kde: bool = True) -> None:
    if kde:
        ox = np.linspace(*xlim, num=granularity)
        kde_ox = gaussian_kde(data_ox)
        ox_interp = kde_ox(ox)

        # ensure densities begin and end in zeroes
        ox_interp = np.insert(
            ox_interp, [0, len(ox)], 0)
        ox = np.insert(ox, [0, len(ox)], xlim)

        ax.plot(
            ox, ox_interp,
            color=VIRIDIS_COLOR,
        )
        ax.fill_between(
            ox, ox_interp, 0,
            color=VIRIDIS_COLOR,
            alpha=.4
        )
    else:
        # Histogram
        ax.hist(
            data_ox, density=True,
            bins=bins, range=xlim,
            color=VIRIDIS_COLOR,
            edgecolor=VIRIDIS_COLOR,
            alpha=.5, linewidth=0
        )

    # median
    xmed = np.nanmedian(data_ox)
    ax.axvline(
        xmed, color=VIRIDIS_COLOR, lw=2, ls="--")
    ax.text(
        xmed,
        ax.get_ylim()[1] +
        ax.get_ylim()[1] * .45,
        f"{xmed:.2f}", color=VIRIDIS_COLOR,
        ha="center", va="top",
        fontweight="bold"
    )

    # plot properties
    ax.set_xlim(*xlim)
    ax.set_title(title, pad=20)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plot_Py(ax: plt.Axes,
            data_oy: np.array,
            ylim: Tuple[float],
            bins: int = 10,
            granularity: int = 100,
            kde: bool = True) -> None:
    if kde:
        oy = np.linspace(*ylim, num=granularity)
        kde_oy = gaussian_kde(data_oy)
        oy_interp = kde_oy(oy)

        # ensure densities begin and end in zeroes
        oy_interp = np.insert(
            oy_interp, [0, len(oy)], 0)
        oy = np.insert(oy, [0, len(oy)], ylim)

        ax.plot(
            oy_interp, oy,
            color=VIRIDIS_COLOR,
        )

        ax.fill_between(
            oy_interp, oy, 0,
            color=VIRIDIS_COLOR,
            alpha=.4
        )
    else:
        ax.hist(
            data_oy, density=True,
            bins=bins, range=ylim,
            color=VIRIDIS_COLOR,
            edgecolor=VIRIDIS_COLOR,
            alpha=.5, orientation="horizontal",
            linewidth=0
        )

    # median
    ymed = np.nanmedian(data_oy)
    ax.axhline(
        ymed, color=VIRIDIS_COLOR, lw=2, ls="--")
    ax.text(
        ax.get_xlim()[1] +
        ax.get_xlim()[1] * .01,
        ymed, f"{ymed:.1f}",
        color=VIRIDIS_COLOR,
        ha="left", va="center",
        fontweight="bold",
        rotation=-90
    )

    # plot properties
    ax.set_ylim(*ylim)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plot_Pxy(ax: plt.Axes, data: np.ndarray,
             xlim: Tuple[float], ylim: Tuple[float],
             xlabel: str, ylabel: str,
             bins: Tuple[int, int] = (10, 10),
             xticks: bool = True,
             yticks: bool = True,
             vmin: float = None,
             vmax: float = None):
    H, xedges, yedges, _ = ax.hist2d(
        data[0], data[1], density=True,
        bins=bins, range=(xlim, ylim),
        vmin=vmin, vmax=vmax
    )

    # OY ticks
    if yticks:
        ax.yaxis.set_major_locator(
            ticker.MultipleLocator(2))
        ax.set_ylabel(ylabel)
    else:
        ax.yaxis.set_major_formatter("")

    # OX ticks
    ax.set_xticks(np.linspace(*xlim, num=bins[0]+1))
    if xticks:
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.set_xticklabels([])

    # plot properties
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel)

    return H, xedges, yedges


def cond_stats(H: np.ndarray,
               xedges: np.array,
               yedges: np.array):
    # x_centers = (xedges[:-1] + xedges[1:])/2
    # y_centers = (yedges[:-1] + yedges[1:])/2

    x_centers = np.linspace(xedges[0], xedges[-1], num=len(xedges)-1)
    y_centers = np.linspace(yedges[0], yedges[-1], num=len(yedges)-1)

    # Probabilities
    dx = (xedges[1] - xedges[0])
    dy = (yedges[1] - yedges[0])

    bin_area = dx * dy
    P_H = H * bin_area

    # P(X|Y)
    x_means, x_devs, x_medians, x_q25, x_q75 =\
        list(), list(), list(), list(), list()
    for i in range(H.shape[1]):
        if P_H[:, i].sum() > 5e-2:
            p_x_given_y = P_H[:, i] / P_H[:, i].sum()

            # Mean
            x_mu = np.sum(x_centers * p_x_given_y)
            x_std = np.sqrt(np.sum(p_x_given_y * (
                x_centers - x_mu) * (x_centers - x_mu)))
            x_means.append(x_mu)
            x_devs.append(x_std)

            # Quantiles
            cdf = np.cumsum(p_x_given_y)
            median = np.interp(0.5, cdf, x_centers)
            q25 = np.interp(0.25, cdf, x_centers)
            q75 = np.interp(0.75, cdf, x_centers)

            x_medians.append(median)
            x_q25.append(q25)
            x_q75.append(q75)
        else:
            x_means.append(np.nan)
            x_devs.append(np.nan)
            x_medians.append(np.nan)
            x_q25.append(np.nan)
            x_q75.append(np.nan)

    # P(Y|X)
    y_means, y_devs, y_medians, y_q25, y_q75 =\
        list(), list(), list(), list(), list()
    for i in range(H.shape[0]):
        if P_H[i].sum() > 5e-2:
            p_y_given_x = P_H[i] / P_H[i].sum()

            # Mean
            y_mu = np.sum(y_centers * p_y_given_x)
            y_std = np.sqrt(np.sum(p_y_given_x * (
                y_centers - y_mu) * (y_centers - y_mu)))
            y_means.append(y_mu)
            y_devs.append(y_std)

            # Quantiles
            cdf = np.cumsum(p_y_given_x)
            median = np.interp(0.5, cdf, y_centers)
            q25 = np.interp(0.25, cdf, y_centers)
            q75 = np.interp(0.75, cdf, y_centers)

            y_medians.append(median)
            y_q25.append(q25)
            y_q75.append(q75)
        else:
            y_means.append(np.nan)
            y_devs.append(np.nan)
            y_medians.append(np.nan)
            y_q25.append(np.nan)
            y_q75.append(np.nan)

    x_means = np.asarray(x_means)
    x_devs = np.asarray(x_devs)
    x_q25 = np.asarray(x_q25)
    x_medians = np.asarray(x_medians)
    x_q75 = np.asarray(x_q75)

    y_means = np.asarray(y_means)
    y_devs = np.asarray(y_devs)
    y_q25 = np.asarray(y_q25)
    y_medians = np.asarray(y_medians)
    y_q75 = np.asarray(y_q75)

    return x_centers, x_means, x_devs, x_q25, x_medians, x_q75, \
        y_centers, y_means, y_devs, y_q25, y_medians, y_q75


def plot_cond_stats(ax: plt.Axes,
                    H: np.ndarray,
                    xedges: np.array,
                    yedges: np.array):
    x_centers, x_means, x_devs, x_q25, x_medians, x_q75, \
        y_centers, y_means, y_devs, y_q25, y_medians, y_q75 = cond_stats(
            H, xedges, yedges)

    # P(X|Y)
    # Medians & Q1-Q3
    ax.plot(x_medians, y_centers, color="r",
            label="Median(Accuracy | Trials)")
    ax.fill_betweenx(
        y_centers, x_q25, x_q75, color="r",
        label="25th-75th percentile (Accuracy | Trials)",
        alpha=0.25
    )
    # Means & Std
    # ax.plot(x_means, y_centers, color="r",
    #         linestyle="--", label="Mean(Accuracy | Trials)")
    # ax.fill_betweenx(
    #     y_centers, x_means + x_devs, x_means - x_devs,
    #     color="r", label="Std (Accuracy | Trials)",
    #     alpha=0.25
    # )

    # P(Y|X)
    # Medians & Q1-Q3
    ax.plot(x_centers, y_medians, color="cyan",
            label="Median(Trials | Accuracy)")
    ax.fill_between(
        x_centers, y_q25, y_q75, color="cyan",
        label="25th-75th percentile (Trials | Accuracy)",
        alpha=0.25
    )
    # Means & Std
    # ax.plot(x_centers, y_means, color="cyan",
    #         linestyle="--", label="Median(Trials | Accuracy)")
    # ax.fill_between(
    #     x_centers, y_means + y_devs, y_means - y_devs,
    #     color="cyan", label="Std (Trials | Accuracy)",
    #     alpha=0.25
    # )

    ax.legend(fontsize=8)


def plot_cbar(ax: plt.Axes, vmin: float,
              vmax: float, fig: plt.Figure) -> None:
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sm = cm.ScalarMappable(cmap="viridis", norm=norm)
    fig.colorbar(sm, cax=ax)


parser = argparse.ArgumentParser()

parser_io = parser.add_argument_group(
    "I/O options")
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

parser_hist = parser.add_argument_group(
    "Histogram settings")
parser_hist.add_argument(
    "-bins", type=int, nargs=2,
    help="Histogram bins (OX, OY)",
    required=True, dest="bins"
)
parser_hist.add_argument(
    "-vmin", type=float,
    help="Minimum density to plot. " +
    "If not specified it will be inferred from data",
    required=False, dest="vmin",
    default=None
)
parser_hist.add_argument(
    "-vmax", type=float,
    help="Maximum density to plot. " +
    "If not specified it will be inferred from data",
    required=False, dest="vmax",
    default=None
)

parser_plot = parser.add_argument_group(
    "Plot settings")
parser_plot.add_argument(
    "-xlim", type=float, nargs=2,
    help="OX limits",
    required=False, dest="xlim",
    default=(0.2, 1)
)
parser_plot.add_argument(
    "-ylim", type=int, nargs=2,
    help="OY limits",
    required=False, dest="ylim",
    default=(1, 10)
)
parser_plot.add_argument(
    "-titles",
    help="Whether to include titles or not",
    action="store_true",
    dest="titles",
    default=False
)
parser_plot.add_argument(
    "-xlabel",
    help="Whether to include the OX label or not",
    action="store_true",
    dest="xlabel",
    default=False
)
parser_plot.add_argument(
    "-cond",
    help="Whether to include conditional medians and interquartile range",
    action="store_true",
    dest="cond",
    default=False
)


if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()
    xlabel = "Obtained accuracies" if args.xlabel else ""
    ylabel = "Required trials"

    # output dir
    out_path = Path(args.out_path)
    os.makedirs(os.path.dirname(
        out_path), exist_ok=True)

    # Load data
    df = pd.read_csv(args.in_path, index_col=0).dropna()
    n_elects = int(df["ES"].iloc[0])

    # Compute minimum and maximum densities
    vmin, vmax = 0, 0
    for os_idx, os_name in enumerate(STRATEGIES):
        # (2, n_samples)
        data_os = df.loc[
            df["Strategy"] == os_name,
            ["ObtainedAcc", "RequiredTrials"]
        ].to_numpy().T

        # Joint distribution
        H, _, _, _ = plt.hist2d(
            data_os[0], data_os[1], density=True,
            bins=args.bins, range=(args.xlim, args.ylim)
        )

        H_min, H_max = H.min(), H.max()
        vmin = H_min if vmin > H_min else vmin
        vmax = H_max if vmax < H_max else vmax

        plt.clf()

    # Plot histograms
    fig = plt.figure(figsize=(22, 5))
    axs = gen_axes_layout(fig, STRATEGIES)

    vmin = vmin if args.vmin is None else args.vmin
    vmax = vmax if args.vmax is None else args.vmax
    for os_idx, os_name in enumerate(STRATEGIES):
        # (2, n_samples)
        data_os = df.loc[
            df["Strategy"] == os_name,
            ["ObtainedAcc", "RequiredTrials"]
        ].to_numpy().T

        # Prioris
        plot_Px(axs[f"{os_name}_Px"], data_os[0],
                os_name if args.titles else "",
                args.xlim, bins=args.bins[0])
        plot_Py(axs[f"{os_name}_Py"], data_os[1],
                args.ylim, bins=args.bins[1])

        # Joint distribution
        H, xedges, yedges = plot_Pxy(
            axs[f"{os_name}_Pxy"], data_os,
            args.xlim, args.ylim, xlabel,
            ylabel, bins=args.bins,
            yticks=(os_idx == 0),
            vmin=vmin, vmax=vmax
        )

        if args.cond:
            plot_cond_stats(
                axs[f"{os_name}_Pxy"], H,
                xedges, yedges
            )

    plot_cbar(axs["Cbar"], vmin, vmax, fig)

    # Text with number of electrodes
    fig.text(.9875, .35, f"{n_elects} electrodes", rotation=270)

    fig.tight_layout()
    save_plot(out_path)
