'''
This script will plot stem plots representing
different divergences' distances between a reference
distribution (ITR) and different alpha configs.
from:
    alpha x Gain + (1 - alpha) Cons

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 27/11/2025
'''

import re
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Tuple
from plots import save_plot
from scipy.stats import entropy
import matplotlib.pyplot as plt
from constants import FONT_SIZE, SEED
from scipy.stats import wasserstein_distance_nd
from scipy.spatial.distance import jensenshannon

plt.rcParams.update({
    'font.size': FONT_SIZE/1.75,
    'font.family': 'Times New Roman'
})

DROP_STRAT = [
    "¾Gain + ¼Cons",
    "½Gain + ½Cons",
    "¼Gain + ¾Cons"
]

# NOTE: Wasserstein's distance does not scale well with high samples.
N_MAX = 500  # Maximum number of samples to consider


# NOTE: We only pay attention to 4th quadrant
# (highest accuracies and fewest trials)
XRANGE = (0, 1)
YRANGE = (1, 10)
BINS = {
    "Hoffmann": (5, 9),
    "Won": (4, 9),
    "WonRCP2RSVP": (4, 9),
}


def js_dist(X: np.ndarray,
            Y: np.ndarray,
            bins: Tuple[int, int]) -> float:
    '''
    Jensen-Shannon divergence computation from
    2D-distributions samples.

    :param X: Sample from 2D distribution with shape:
        (n_samples_X, 2)
    :param Y: Sample from 2D distribution with shape:
        (n_samples_Y, 2)
    :param bins: Tuple with bin sizes for each dimension.

    :return float: Jensen-Shannon divergence between
    X-Y distributions.
    '''
    # Histograms
    H_X, xedges, yedges = np.histogram2d(
        X[:, 0], X[:, 1], bins=bins, density=True,
        range=(XRANGE, YRANGE)
    )
    H_Y, _, _ = np.histogram2d(
        Y[:, 0], Y[:, 1], bins=[xedges, yedges],
        density=True, range=(XRANGE, YRANGE)
    )

    # Normalization
    dx = (xedges[1] - xedges[0])
    dy = (yedges[1] - yedges[0])
    bin_area = dx * dy

    # Probabilities
    P_X = (H_X * bin_area)
    P_Y = (H_Y * bin_area)

    return jensenshannon(P_X.ravel(), P_Y.ravel())


def kl_div(X: np.ndarray,
           Y: np.ndarray,
           bins: Tuple[int, int],
           eps: float = 1e-10) -> float:
    '''
    Kullback-Leibler divergence computation from
    2D-distributions samples.

    :param X: Sample from 2D distribution with shape:
        (n_samples_X, 2)
    :param Y: Sample from 2D distribution with shape:
        (n_samples_Y, 2)
    :param bins: Tuple with bin sizes for each dimension.
    :param eps: Minimum value to avoid zero probabilities,
    defaults to `1e-10`.

    :return float: Kullback-Leibler divergence between
    X-Y distributions.
    '''
    # Histograms
    H_X, xedges, yedges = np.histogram2d(
        X[:, 0], X[:, 1], bins=bins, density=True,
        range=(XRANGE, YRANGE)
    )
    H_Y, _, _ = np.histogram2d(
        Y[:, 0], Y[:, 1], bins=[xedges, yedges],
        density=True, range=(XRANGE, YRANGE)
    )

    # Normalization
    dx = (xedges[1] - xedges[0])
    dy = (yedges[1] - yedges[0])
    bin_area = dx * dy

    # Probabilities
    P_X = (H_X * bin_area) + eps
    P_Y = (H_Y * bin_area) + eps

    # Renormalization
    P_X = P_X / P_X.sum()
    P_Y = P_Y / P_Y.sum()

    return entropy(P_X.ravel(), P_Y.ravel())


parser = argparse.ArgumentParser()

parser_io = parser.add_argument_group("I/O Options")
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

parser_strat = parser.add_argument_group(
    "Strategy options")
parser_strat.add_argument(
    "-ess", "--early-stop", nargs='+',
    help="Early stop strategy to fix",
    required=True, dest="ess"
)
parser_strat.add_argument(
    "-erpd", "--erp-detector", nargs='+',
    help="ERP detector to fix",
    required=True, dest="erpd"
)
parser_strat.add_argument(
    "-ds", "--dataset",
    help="Dataset to fix",
    required=True, dest="ds"
)

parser_plot = parser.add_argument_group("Plot options")
parser_plot.add_argument(
    "-t", "--title", type=str,
    help="Extra message to add on the title, e.g. the dataset name",
    required=True, dest="title"
)
parser_plot.add_argument(
    "-m", "--measure",
    help="Measure to compare distributions",
    choices=["Wasserstein", "Kullback-Leibler", "Jensen-Shannon Distance"],
    required=True, dest="measure"
)

parser_extra = parser.add_argument_group("Additional options")
parser_extra.add_argument(
    "-s", "--seed", type=int,
    help="Seed to choose random samples " +
    "(only useful for Wasserstein distance)",
    required=False, dest="seed",
    default=SEED
)

if __name__ == "__main__":
    # Parse arguments
    args = parser.parse_args()

    # Load results
    df = pd.read_csv(args.in_path, index_col=0).dropna()
    df = df[(df["ESS"].isin(args.ess)) &
            (df["ERPd"].isin(args.erpd)) &
            (df["Dataset"] == args.ds)]

    # Get rid of fractional codes (to have the same sample size)
    df = df.drop(df[df["Strategy"].isin(DROP_STRAT)].index)

    # GCB decimal values to alphas (this changes strategies' names)
    optim_strats = np.sort(list(df["Strategy"].unique()))
    filt_gcb = re.compile(r".*Gain.*Cons")
    filt_strats = list(filter(filt_gcb.search, optim_strats))

    alphas = [float(re.match("([0-9.]+)Gain", strat).group(1))
              for strat in filt_strats]

    for i, os in enumerate(filt_strats):
        df.loc[df["Strategy"] == os, "Strategy"] = alphas[i]

    # Divergence computation
    os_blne = "ITR"  # Reference distribution
    OA_blne = df[df["Strategy"] == os_blne]["ObtainedAcc"]
    RT_blne = df[df["Strategy"] == os_blne]["RequiredTrials"]
    dist_blne = np.stack((OA_blne, RT_blne), axis=1)

    if args.measure == "Wasserstein":
        # random subset
        np.random.seed(args.seed)
        np.random.shuffle(dist_blne)
        dist_blne = dist_blne[:N_MAX]

    # remove ITR from the comparison set
    optim_strats = np.sort(
        df.loc[df["Strategy"] != "ITR", "Strategy"].unique())
    scores = np.zeros(len(optim_strats))
    for i, os in tqdm(enumerate(optim_strats)):
        OA_curr = df[df["Strategy"] == os]["ObtainedAcc"]
        RT_curr = df[df["Strategy"] == os]["RequiredTrials"]
        dist_curr = np.stack((OA_curr, RT_curr), axis=1)

        if args.measure == "Wasserstein":
            # random subset
            np.random.shuffle(dist_curr)
            dist_curr = dist_curr[:N_MAX]
            scores[i] = wasserstein_distance_nd(dist_blne, dist_curr)
        elif args.measure == "Kullback-Leibler":
            scores[i] = kl_div(dist_blne, dist_curr, bins=BINS[args.ds])
        elif args.measure == "Jensen-Shannon Distance":
            scores[i] = js_dist(dist_blne, dist_curr, bins=BINS[args.ds])
        else:
            raise Exception(f"Unknown measure {args.measure}")

    idxs_sort = np.argsort(scores)
    optim_strats_sort = optim_strats[idxs_sort]
    scores_sort = scores[idxs_sort]

    print(f"Baseline strategy: {os_blne}")
    print(f"Alpha ranking: {optim_strats_sort}")

    # Plots
    plt.stem(optim_strats_sort, scores_sort)
    plt.plot(optim_strats, scores, color="#D62728")

    plt.xlabel("Alpha")
    plt.ylabel(f"{args.measure} measure")
    plt.title(f"Baseline distribution: {os_blne} — {args.title}")

    plt.tight_layout()

    save_plot(args.out_path)
