"""
This script will try reproducing the
Information Transfer Rate function by
means of a non-linear function in terms
of different Gain and Conservation weights.

:Author: Javier Jiménez Rodríguez
(javier.jimenez02@estudiante.uam.es)
:Date: 07/05/2025
"""

import re
import argparse
import numpy as np
from typing import Tuple
from pathlib import Path
from plots import save_plot
from functools import partial
from metrics import (bcim_gc,
                     gcb,
                     itr,
                     spm,
                     bci_utility)
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase
from constants import HOFF_TRIAL_EPOCHS, HOFF_ISI, FONT_SIZE

plt.rcParams.update({
    'font.size': FONT_SIZE/1.5,
    'font.family': 'Times New Roman'
})
CMAPS = ["viridis", "plasma", "cividis"]
CMAPS_FN = [plt.cm.viridis, plt.cm.plasma, plt.cm.cividis]
ALPHA = .8


class HandlerColormap(HandlerBase):
    """
    Adapted from:
    https://stackoverflow.com/questions/55501860/how-to-put-multiple-colormap-patches-in-a-matplotlib-legend
    """

    def __init__(self, cmap, num_stripes=8, **kw):
        HandlerBase.__init__(self, **kw)
        self.cmap = cmap
        self.num_stripes = num_stripes

    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        stripes = []
        for i in range(self.num_stripes):
            s = Rectangle([xdescent + i * width / self.num_stripes, ydescent],
                          width / self.num_stripes,
                          height,
                          fc=self.cmap((2 * i + 1) / (2 * self.num_stripes)),
                          transform=trans)
            stripes.append(s)
        return stripes


# Linear (basic)
def gcb_lin(
        X: Tuple[float, float],
        a: float, b: float) -> float:
    G, C = X
    return a*G + b*C


# GCB Exponential (non-linear)
def gcb_exp(
        X: Tuple[float, float],
        a: float, b: float,
        c: float, d: float) -> float:
    G, C = X
    return d + c * np.exp(G * a + C * b)


# GCB Potential (non-linear)
def gcb_pot(
        X: Tuple[float, float],
        a: float, b: float,
        c: float, d: float,
        e: float) -> float:
    G, C = X
    return e + c*(G**a) + d*(C**b)


def plot_bcimes_vs_bcimod(
        ax: plt.Axes, xx: np.ndarray, yy: np.ndarray,
        zz: np.ndarray, zz_pred: np.ndarray,
        title: str, bcimes: str, bcimod: str,
        n_classes: int, trial_secs: float,
        t_base: int, acc_base: float):

    # colormap normalization
    vmin = min(np.min(zz), np.min(zz_pred))
    vmax = max(np.max(zz), np.max(zz_pred))
    norm = Normalize(vmin=vmin, vmax=vmax)

    # original
    surf1 = ax.plot_surface(
        xx, yy, zz, cmap=CMAPS[0],
        norm=norm, alpha=ALPHA
    )
    # estimated
    surf2 = ax.plot_surface(
        xx, yy, zz_pred, cmap=CMAPS[1],
        norm=norm, alpha=ALPHA
    )

    # for optimization purposes
    surf1.set_rasterized(True)
    surf2.set_rasterized(True)

    # labels
    if title is not None:
        ax.set_title(f"{title} experiment " +
                     f"— {bcimes} estimation with " +
                     f"{bcimod} model")
    else:
        ax.set_title(
            f"{bcimes} estimation with {bcimod} model")
    ax.set_xlabel("Gain", labelpad=10)
    ax.set_ylabel("Cons", labelpad=10)
    ax.set_zlabel(bcimes, labelpad=10)
    ax.set_zlim(vmin, vmax)
    ax.invert_xaxis()

    # fancy legend
    cmap_labels = [bcimes, bcimod]
    # create proxy artists as handles:
    cmap_handles = [Rectangle((0, 0), 1, 1) for _ in CMAPS_FN[:2]]
    handler_map = dict(zip(cmap_handles, [
        HandlerColormap(cm, num_stripes=8) for cm in CMAPS_FN[:2]]))
    ax.legend(handles=cmap_handles,
              labels=cmap_labels,
              handler_map=handler_map,
              loc="upper right", bbox_to_anchor=(.85, .6))

    # parameters text-box
    textstr = '\n'.join((
        f"Available classes: {n_classes}",
        f"Trial duration: {trial_secs}s",
        f"Baseline trials: {t_base}",
        f"Baseline accuracy: {acc_base}",
    ))
    ax.text2D(
        x=0.5, y=0.75, s=textstr,
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=FONT_SIZE/1.5,
        bbox={"boxstyle": "round", "alpha": .5, "facecolor": "white"}
    )

    # orientation and layout adjustment
    ax.view_init(20, -60, 0)


def plot_bcimes_vs_bcimod_sqerr(
        ax: plt.Axes, xx: np.ndarray, yy: np.ndarray,
        zz: np.ndarray, zz_pred: np.ndarray,
        title: str, bcimes: str, bcimod: str,
        n_classes: int, trial_secs: float,
        t_base: int, acc_base: float):

    # Absolute error
    sqerr = np.abs(zz - zz_pred)
    surf = ax.plot_surface(
        xx, yy, sqerr, cmap=CMAPS[2], alpha=ALPHA)

    # for optimization purposes
    surf.set_rasterized(True)

    # labels
    if title is not None:
        ax.set_title(f"{title} experiment " +
                     f"— |{bcimes} - {bcimod}|")
    else:
        ax.set_title(
            f"Absolute Error — |{bcimes} - {bcimod}|")
    ax.set_xlabel("Gain", labelpad=10)
    ax.set_ylabel("Cons", labelpad=10)
    ax.set_zlabel("Absolute Error", labelpad=25)
    ax.tick_params(axis='z', pad=10)
    ax.set_zlim(0, None)
    ax.invert_xaxis()

    # fancy legend
    cmap_labels = ["Absolute Error"]
    # create proxy artists as handles:
    cmap_handles = [Rectangle((0, 0), 1, 1)]
    handler_map = dict(zip(cmap_handles, [HandlerColormap(
        CMAPS_FN[2], num_stripes=8)]))
    ax.legend(handles=cmap_handles,
              labels=cmap_labels,
              handler_map=handler_map,
              loc="upper right", bbox_to_anchor=(.85, .6))

    # parameters text-box
    textstr = '\n'.join((
        f"Available classes: {n_classes}",
        f"Trial duration: {trial_secs}s",
        f"Baseline trials: {t_base}",
        f"Baseline accuracy: {acc_base}",
    ))
    ax.text2D(
        x=0.5, y=0.75, s=textstr,
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=FONT_SIZE/1.5,
        bbox={"boxstyle": "round", "alpha": .5, "facecolor": "white"}
    )

    # orientation and layout adjustment
    ax.view_init(20, -60, 0)


BCI_MODELS = {  # alongwith their print functions
    "Linear": (gcb_lin, lambda bcimes, a, b:
               f"{a:.4f}Gain + {b:.4f}Cons = {bcimes}"),
    "Exponential": (gcb_exp, lambda bcimes, a, b, c, d:
                    f"{d:.4f} + {c:.4f}exp({a:.4f}Gain + " +
                    f"{b:.4f}Cons) = {bcimes}"),
    "Potential": (gcb_pot, lambda bcimes, a, b, c, d, e:
                  f"{e:.4f} + {c:.4f}Gain^{a:.4f} + " +
                  f"{d:.4f}Cons^{b:.4f} = {bcimes}"),
}
GCB_REGEXP = re.compile(
    r".Gain \+ .Cons")
BCI_MEASURES = {
    "ITR": itr,
    "SPM": spm,
    "BCI Utility": bci_utility,
    "¾Gain + ¼Cons": partial(
        gcb, weights=(0.75, 0.25)),
    "½Gain + ½Cons": partial(
        gcb, weights=(0.5, 0.5)),
    "¼Gain + ¾Cons": partial(
        gcb, weights=(0.25, 0.75))
}

parser = argparse.ArgumentParser()

parser_grid = parser.add_argument_group("Grid settings")
parser_grid.add_argument(
    "-n", "-n-samples", type=int,
    help="Grid size",
    required=False, dest="n",
    default=100
)

parser_bbci = parser.add_argument_group("Baseline BCI")
parser_bbci.add_argument(
    "-tmax", type=int,
    help="Maximum amount of trials of the baseline BCI",
    required=False, dest="tmax",
    default=20
)
parser_bbci.add_argument(
    "-accmax", type=float,
    help="Accuracy obtained by the baseline BCI (in [0, 1])",
    required=False, dest="accmax",
    default=1
)

parser_bcim = parser.add_argument_group("BCI Model")
parser_bcim.add_argument(
    "-bcimes", type=str,
    help="BCI measure to reproduce in terms of Gain & Cons",
    required=True, dest="bcimes",
    choices=BCI_MEASURES.keys()
)
parser_bcim.add_argument(
    "-bcimod", type=str,
    help="BCI model to employ",
    required=True, dest="bcimod",
    choices=BCI_MODELS.keys()
)

parser_expr = parser.add_argument_group("BCI Experiment")
parser_expr.add_argument(
    "-c", "--classes", type=int,
    help="Number of possible classes (i.e. stimuli per trial)",
    required=False, dest="n_classes",
    default=HOFF_TRIAL_EPOCHS
)
parser_expr.add_argument(
    "-ts", "--trial-secs", type=float,
    help="Duration of a trial in seconds",
    required=False, dest="trial_secs",
    default=HOFF_TRIAL_EPOCHS * (HOFF_ISI/1e3)
)

parser_plot = parser.add_argument_group("Plots")
parser_plot.add_argument(
    "-p", "--plot",
    action="store_true",
    help="If this flag is specified, the algorithm " +
    "will plot the original surface plot and the estimated one.",
    default=False, required=False, dest="plot"
)
parser_plot.add_argument(
    "-t", "--title", type=str,
    help="Extra header for the title.",
    required=False, default=None, dest="title"
)
parser_plot.add_argument(
    "-o", "--output", type=str,
    help="Directory path in which the plot will be stored",
    required=False, default=None, dest="out_path"
)

if __name__ == "__main__":
    args = parser.parse_args()

    # Grid obtainance — lower bounds aren't zero to avoid zero divisions
    xx, yy = np.meshgrid(
        # Gain values — (upper bound at the first trial as we
        # assume we cannot stop earlier)
        np.linspace(5e-1, (args.tmax-1)/args.tmax, args.n),
        # Conservation values
        np.linspace(5e-1, 1, args.n)
    )

    # BCI Measurement
    if GCB_REGEXP.match(args.bcimes) is not None:
        zz = np.vectorize(
            BCI_MEASURES[args.bcimes],
            otypes=[float]
        )(xx, yy)
    else:
        zz = np.vectorize(partial(
            bcim_gc,
            measure=BCI_MEASURES[args.bcimes],
            t_base=args.tmax, acc_base=args.accmax,
            n_classes=args.n_classes,
            trial_secs=args.trial_secs
        ), otypes=[float])(xx, yy)

    # BCI Model
    gcb_mod, gcb_str = BCI_MODELS[args.bcimod]

    # Least Squares estimation
    popt, _ = curve_fit(
        gcb_mod, (xx.flatten(), yy.flatten()),
        zz.flatten()
    )
    print(gcb_str(args.bcimes, *popt))

    # Model predictions
    zz_pred = gcb_mod(
        (xx.flatten(),
         yy.flatten()),
        *popt
    ).reshape((args.n, args.n))

    # R² scores
    r2 = r2_score(
        zz.flatten(),
        zz_pred.flatten()
    )
    print(f"R2 score: {r2:.4f}")

    # Plots
    if args.plot:
        fig, axs = plt.subplots(
            nrows=2, ncols=1,
            subplot_kw={"projection": "3d"},
            figsize=(10, 14)
        )

        plot_bcimes_vs_bcimod(
            axs[0], xx, yy, zz, zz_pred,
            args.title, args.bcimes, args.bcimod,
            args.n_classes, args.trial_secs,
            args.tmax, args.accmax
        )
        plot_bcimes_vs_bcimod_sqerr(
            axs[1], xx, yy, zz, zz_pred,
            args.title, args.bcimes, args.bcimod,
            args.n_classes, args.trial_secs,
            args.tmax, args.accmax
        )

        plt.tight_layout()

        if args.out_path is not None:
            # save figure
            out_dir = Path(args.out_path)
            save_plot(out_dir / f"{args.bcimes}_{args.bcimod}_Model.svg")
        else:
            plt.show()
