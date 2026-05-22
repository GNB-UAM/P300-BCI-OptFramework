# README - Figures
[Return to table of contents](../../README.md).

## Figures' scripts
Particularly, we drew 7 types of figures:
- Speed–Accuracy density maps - 2D Histograms
- Policies average trial–accuracy dots
- Win-Loss-Tie Stacked Bar-Plots
- Conditioned Stacked Bar-Plots
- Conditioned Histograms
- ITR - GCB relationship
- ITR vs. GCB - Jensen–Shannon divergences

> **Note**
> 
> For more information on the meaning of each script argument, consult their help page with `python <script>.py -h`.

### Speed–Accuracy density maps - 2D Histograms
`scripts/plots/optim_strat_2d_hist.py` draws a 2D histogram, called speed–accuracy density maps in the paper, as a function of the paradigm, policy, transducer, and control-interface employed.

Usage example:
```
python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/HoffAll.csv -o results/Optuna/electsets/plots/hoff/HoffAll_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 5 9 -vmin 0 -vmax 1.5
```

### Policies average trial–accuracy dots
`scripts/plots/optim_strat_quad_scatterplot.py` plots the mean and standard deviation of every policy, transducer, and control-interface.

Usage example:
```
python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HoffErrScatt.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -s -ac
```

### Win-Loss-Tie Stacked Bar-Plots
`scripts/plots/winloss_dominance.py` obtains stacked bar-plots with the proportion of win-tie-loss of a policy against three others from all run experiments.

Usage example:
```
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/OA/GCB0.25.svg -m ObtainedAccuracies -s "¼Gain + ¾Cons"
```

### Conditioned Stacked Bar-Plots
`scripts/plots/optim_strat_condsbar.py` displays policy-wise histograms of required trials and obtained accuracy from all run experiments.

Usage example:
```
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m RequiredTrials
```

### Conditioned Histograms
`scripts/plots/optim_strat_condsbar.py` shows policy-wise histograms of required trials and obtained accuracy from all run experiments after fixing either a minimum accuracy or a maximum number of trials.

Usage example:
```
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HIS/RT/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m RequiredTrials -ylim 0 0.65 -xlim 0 1 -bins 5 9
```

### ITR - GCB relationship
`scripts/plots/gcb_bcim_relation.py` estimates the Information Transfer Rate as a function of the Gain–Conservation measurements through least squares and draws it within a 3D-plot.

Usage example:
```
python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 20 -accmax 1.0 -bcimes "ITR" -bcimod "Linear" -c 6 -ts 2.4 -p -o results/INV/ITR_GCB_Repr/hoff -t "Hoffmann"
```

> **Note**
>
> Here no data are needed.

### ITR vs. GCB - Jensen–Shannon divergences
`scripts/plots/ITR_alpha_similarity.py` obtains stem-plots representing Jensen–Shannon divergences between the distribution of experiments optimized with the Information Transfer Rate policy and those optimized with the Gain–Conservation Balance as a function of different $\alpha$ values.

Usage example:
```
python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Hoff_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Hoffmann_KL.svg -t "Hoffmann" -m "Kullback-Leibler" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Hoffmann
```

## What we did
Figures were generated from CSV files, so it is crucial to review [results formatting guidelines](../reports/README.md).

### Speed–Accuracy density maps - 2D Histograms
For Hoffmann:
```sh
python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/HoffAll.csv -o results/Optuna/electsets/plots/hoff/HoffAll_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 5 9 -vmin 0 -vmax 1.5

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Hoff16.csv -o results/Optuna/electsets/plots/hoff/Hoff16_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 5 9 -vmin 0 -vmax 1.5

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Hoff8.csv -o results/Optuna/electsets/plots/hoff/Hoff8_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 5 9 -vmin 0 -vmax 1.5

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Hoff4.csv -o results/Optuna/electsets/plots/hoff/Hoff4_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 5 9 -vmin 0 -vmax 1.5
```

For Won:
```sh
python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/WonAll.csv -o results/Optuna/electsets/plots/won/WonAll_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 4 9 -vmin 0 -vmax 1.25

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Won16.csv -o results/Optuna/electsets/plots/won/Won16_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 4 9 -vmin 0 -vmax 1.25

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Won8.csv -o results/Optuna/electsets/plots/won/Won8_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 4 9 -vmin 0 -vmax 1.25

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/Won4.csv -o results/Optuna/electsets/plots/won/Won4_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 4 9 -vmin 0 -vmax 1.25
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/WonRCP2RSVPAll.csv -o results/Optuna/electsets/plots/wonrcp2rsvp/WonRCP2RSVPAll_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 9 9 -vmin 0 -vmax 2

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/WonRCP2RSVP16.csv -o results/Optuna/electsets/plots/wonrcp2rsvp/WonRCP2RSVP16_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 9 9 -vmin 0 -vmax 2

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/WonRCP2RSVP8.csv -o results/Optuna/electsets/plots/wonrcp2rsvp/WonRCP2RSVP8_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 9 9 -vmin 0 -vmax 2

python scripts/plots/optim_strat_2dhist.py -i results/Optuna/electsets/CSV/WonRCP2RSVP4.csv -o results/Optuna/electsets/plots/wonrcp2rsvp/WonRCP2RSVP4_2DHis.svg -xlim 0 1 -ylim 1 10 -xlabel -bins 9 9 -vmin 0 -vmax 2
```

### Policies average trial–accuracy dots
For Hoffmann:
```sh
python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HoffErrScatt.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HoffErrScatt_LinearSVC.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC -ds Hoffmann -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HoffErrScatt_RandomForest.svg -ess FixedStop AccumEvid StatsTest -erpd RandomForestClassifier -ds Hoffmann -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HoffErrScatt_BLDA.svg -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis -ds Hoffmann -s -ac
```

For Won:
```sh
python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WonErrScatt.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Won -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WonErrScatt_LinearSVC.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC -ds Won -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WonErrScatt_RandomForest.svg -ess FixedStop AccumEvid StatsTest -erpd RandomForestClassifier -ds Won -s -oslcr -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WonErrScatt_BLDA.svg -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis -ds Won -s -ac
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WonRCP2RSVPErrScatt.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds WonRCP2RSVP -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WonRCP2RSVPErrScatt_LinearSVC.svg -ess FixedStop AccumEvid StatsTest -erpd LinearSVC -ds WonRCP2RSVP -s -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WonRCP2RSVPErrScatt_RandomForest.svg -ess FixedStop AccumEvid StatsTest -erpd RandomForestClassifier -ds WonRCP2RSVP -s -oslcr -ac

python scripts/plots/optim_strat_quad_scatterplot.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WonRCP2RSVPErrScatt_BLDA.svg -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis -ds WonRCP2RSVP -s -ac
```

### Win-Loss-Tie Stacked Bar-Plots
For Hoffmann:
```sh
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/OA/GCB0.25.svg -m ObtainedAccuracies -s "¼Gain + ¾Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/RT/GCB0.25.svg -m RequiredTrials -s "¼Gain + ¾Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/OA/GCB0.75.svg -m ObtainedAccuracies -s "¾Gain + ¼Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/RT/GCB0.75.svg -m RequiredTrials -s "¾Gain + ¼Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/OA/GCB0.50.svg -m ObtainedAccuracies -s "½Gain + ½Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/RT/GCB0.50.svg -m RequiredTrials -s "½Gain + ½Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/OA/ITR.svg -m ObtainedAccuracies -s "ITR"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/WLDom/RT/ITR.svg -m RequiredTrials -s "ITR"
```

For Won:
```sh
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/OA/GCB0.25.svg -m ObtainedAccuracies -s "¼Gain + ¾Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/RT/GCB0.25.svg -m RequiredTrials -s "¼Gain + ¾Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/OA/GCB0.75.svg -m ObtainedAccuracies -s "¾Gain + ¼Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/RT/GCB0.75.svg -m RequiredTrials -s "¾Gain + ¼Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/OA/GCB0.50.svg -m ObtainedAccuracies -s "½Gain + ½Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/RT/GCB0.50.svg -m RequiredTrials -s "½Gain + ½Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/OA/ITR.svg -m ObtainedAccuracies -s "ITR"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/WLDom/RT/ITR.svg -m RequiredTrials -s "ITR"
```

For Stimulus-Level Won:
```sh
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/OA/GCB0.25.svg -m ObtainedAccuracies -s "¼Gain + ¾Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/RT/GCB0.25.svg -m RequiredTrials -s "¼Gain + ¾Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/OA/GCB0.75.svg -m ObtainedAccuracies -s "¾Gain + ¼Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/RT/GCB0.75.svg -m RequiredTrials -s "¾Gain + ¼Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/OA/GCB0.50.svg -m ObtainedAccuracies -s "½Gain + ½Cons"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/RT/GCB0.50.svg -m RequiredTrials -s "½Gain + ½Cons"

python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/OA/ITR.svg -m ObtainedAccuracies -s "ITR"
python scripts/plots/winloss_dominance.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/WLDom/RT/ITR.svg -m RequiredTrials -s "ITR"
```

### Conditioned Stacked Bar-Plots
#### Condition Speed
For Hoffmann:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m RequiredTrials
```

For Won:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Won -m RequiredTrials
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds WonRCP2RSVP -m RequiredTrials
```

#### Condition Accuracy
For Hoffmann:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m ObtainedAccuracies
```

For Won:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Won -m ObtainedAccuracies
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_condsbar.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds WonRCP2RSVP -m ObtainedAccuracies
```

### Conditioned Histograms
#### Condition Speed
For Hoffmann:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HIS/RT/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m RequiredTrials -ylim 0 0.65 -xlim 0 1 -bins 5 9
```

For Won:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/HIS/RT/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Won -m RequiredTrials -ylim 0 0.65 -xlim 0 1 -bins 4 9
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/HIS/RT/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds WonRCP2RSVP -m RequiredTrials -ylim 0 0.65 -xlim 0 1 -bins 9 9
```

##### Condition Accuracy
For Hoffmann:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/HoffAll.csv -o results/Optuna/OptimCVComplete/plots/hoff/HIS/OA/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Hoffmann -m ObtainedAccuracies -ylim 0 0.4 -xlim 1 10 -bins 5 9
```

For Won:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/WonAll.csv -o results/Optuna/OptimCVComplete/plots/won/HIS/OA/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds Won -m ObtainedAccuracies -ylim 0 0.4 -xlim 1 10 -bins 4 9
```

For Stimulus-Level Won:
```sh
python scripts/plots/optim_strat_condhis.py -i results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv -o results/Optuna/OptimCVComplete/plots/wonrcp2rsvp/HIS/OA/ -ess FixedStop AccumEvid StatsTest -erpd LinearSVC RandomForestClassifier LinearDiscriminantAnalysis -ds WonRCP2RSVP -m ObtainedAccuracies -ylim 0 0.4 -xlim 1 10 -bins 9 9
```

### ITR - GCB relationship
Hoffmann:
```sh
python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 20 -accmax 1.0 -bcimes "ITR" -bcimod "Linear" -c 6 -ts 2.4 -p -o results/INV/ITR_GCB_Repr/hoff -t "Hoffmann"

python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 20 -accmax 1.0 -bcimes "ITR" -bcimod "Potential" -c 6 -ts 2.4 -p -o results/INV/ITR_GCB_Repr/hoff -t "Hoffmann"

python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 20 -accmax 1.0 -bcimes "ITR" -bcimod "Exponential" -c 6 -ts 2.4 -p -o results/INV/ITR_GCB_Repr/hoff -t "Hoffmann"
```

Won:
```sh
python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 15 -accmax 1.0 -bcimes "ITR" -bcimod "Linear" -c 36 -ts 2.1876 -p -o results/INV/ITR_GCB_Repr/won -t "Won"

python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 15 -accmax 1.0 -bcimes "ITR" -bcimod "Potential" -c 36 -ts 2.1876 -p -o results/INV/ITR_GCB_Repr/won -t "Won"

python scripts/plots/gcb_bcim_relation.py -n 1000 -tmax 15 -accmax 1.0 -bcimes "ITR" -bcimod "Exponential" -c 36 -ts 2.1876 -p -o results/INV/ITR_GCB_Repr/won -t "Won"
```

### ITR vs. GCB - Jensen–Shannon divergences
For Hoffmann:
```sh
python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Hoff_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Hoffmann_KL.svg -t "Hoffmann" -m "Kullback-Leibler" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Hoffmann

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Hoff_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Hoffmann_W.svg -t "Hoffmann" -m "Wasserstein" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Hoffmann

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Hoff_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Hoffmann_JS.svg -t "Hoffmann" -m "Jensen-Shannon Distance" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Hoffmann
```

For Won:
```sh
python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Won_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Won_KL.svg -t "Won" -m "Kullback-Leibler" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Won

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Won_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Won_W.svg -t "Won" -m "Wasserstein" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Won

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/Won_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/Won_JS.svg -t "Won" -m "Jensen-Shannon Distance" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds Won
```

For Stimulus-Level Won:
```sh
python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/WonRCP2RSVP_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/WonRCP2RSVP_KL.svg -t "WonRCP2RSVP" -m "Kullback-Leibler" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds WonRCP2RSVP

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/WonRCP2RSVP_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/WonRCP2RSVP_W.svg -t "WonRCP2RSVP" -m "Wasserstein" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds WonRCP2RSVP

python scripts/plots/ITR_alpha_similarity.py -i results/ITR_GCB_Repr/CSV/WonRCP2RSVP_ITR_GCB_Repr.csv -o results/ITR_GCB_Repr/plots/WonRCP2RSVP_JS.svg -t "WonRCP2RSVP" -m "Jensen-Shannon Distance" -ess FixedStop AccumEvid StatsTest -erpd LinearDiscriminantAnalysis RandomForestClassifier LinearSVC -ds WonRCP2RSVP
```
