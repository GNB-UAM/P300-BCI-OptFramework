# README - Simulations
[Return to table of contents](../../README.md).

## Simulation script
We ran several simulations with a script called `scripts/simulations/bci_optim.py`.
This script executes the optimization framework shown on the figure above for all paradigm, policy, transducer, and control-interface combinations.

Usage:
```
python scripts/simulations/bci_optim.py -d Hoffmann -s 1 -id preproc/hoff/all -o example -os ITR -erpd LinearDiscriminantAnalysis -j -1 -t 16
```
In this example, the first subject from Hoffmann et al. [^1] experiment (`-d Hoffmann -s 1`) is optimized using all electrodes (`-id preproc/hoff/all`), the Information Transfer Rate as optimization policy (`-os ITR`), and Regularized LDA as transducer (`-erpd LinearDiscriminantAnalysis`).
Moreover, all CPU cores were assigned to work in parallel (`-j -1`) and 16 hyperparameters were assessed (`-t 16`).
This was repeated for every subject, paradigm, electrode subset, transducer, control-interface, and optimization policy.

We also provide a Bash script to execute all simulations across policies, transducers, and control-interfaces automatically: `scripts/simulations/bash/optimize_all_bci.sh`.
Parameters must be provided in this order: `scripts/simulations/bash/optimize_all_bci.sh <optim_script> <dataset> <input_dir> <output_db> <n_jobs>`

Usage example:
```
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/hoff16 "HoffStudy_ElectSet - hoff16" -1
```

### Information Transfer Rate versus Gain–Conservation Balance
Additionally, we also simulated a continuous grid of $\alpha$ values in $[0.5, 1)$ to analyze Gain–Conservation Balance changes as a function of $\alpha$ with: `alpha_bci_optim_grid.sh` 
Parameters must be provided in this order: `scripts/simulations/bash/alpha_bci_optim_grid.sh <optim_script> <dataset> <input_dir> <output_db> <n_jobs>`

Usage example:
```
sh scripts/simulations/bash/alpha_bci_optim_grid.sh scripts/simulations/bci_optim.py Won preproc/won/all Won_ITR_GCB_Repr -1
```

## What we did
Before doing this, it is important to review what we did in the [preprocessing guidelines](../preproc/README.md).

### Generate results for 32 electrodes setup

> **Warning**
>
> This may take a lot of time (>1 week).
> Unless dividing computation charge on multiple PCs or CPUs.

To generate all results from Hoffmann et al. into a file called `HoffStudy.db`:
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/all "HoffStudy" -1
```

To generate all results from Won et. al. into a file called `WonStudy.db`:
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Won preproc/won/all "WonStudy" -1
```

To generate all results from Won et. al. into a file called `WonRCP2RSVStudy.db`: (treating it as a Stimulus-Level paradigm)
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py WonRCP2RSVP preproc/won/all "WonRCP2RSVPStudy" -1
```

All these results were moved into the folder `results/Optuna/OptimCVComplete/<dset>/` to then be translated into CSV files.

### Generate results for the rest of electrodes setups

> **Warning**
>
> This takes some time (<2 days)!

To generate these results from Hoffmann et. al.:
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/hoff16 "HoffStudy_ElectSet - hoff16" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/hoff8 "HoffStudy_ElectSet - hoff8" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/hoff4 "HoffStudy_ElectSet - hoff4" -1
```

To generate all results from Won et. al.:
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Won preproc/won/won16 "WonStudy_ElectSet - won16" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Won preproc/won/won8 "WonStudy_ElectSet - won8" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py Won preproc/won/won4 "WonStudy_ElectSet - won4" -1
```

To generate all results from Won et. al.: (treating it as a Stimulus-Level paradigm)
```sh
sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py WonRCP2RSVP preproc/won/won16 "WonRCP2RSVPStudy_ElectSet - won16" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py WonRCP2RSVP preproc/won/won8 "WonRCP2RSVPStudy_ElectSet - won8" -1

sh scripts/simulations/bash/optimize_all_bci.sh scripts/simulations/bci_optim.py WonRCP2RSVP preproc/won/won4 "WonRCP2RSVPStudy_ElectSet - won4" -1
```

All these results were moved into the folder `results/Optuna/electsets/<dset>/` to then be translated into CSV files.

### ITR reproduction with the GCB

> **Warning**
>
> This takes some time (<2 days)!

Additionally, more combinations of Gain and Cons were evaluated to discern which one obtained the most similar results to the ITR:

For Hoffmann:
```sh
sh scripts/simulations/bash/alpha_bci_optim_grid.sh scripts/simulations/bci_optim.py Hoffmann preproc/hoff/all Hoff_ITR_GCB_Repr -1
```

For Won:
```sh
sh scripts/simulations/bash/alpha_bci_optim_grid.sh scripts/simulations/bci_optim.py Won preproc/won/all Won_ITR_GCB_Repr -1
```

For WonRCP2RSVP:
```sh
sh scripts/simulations/bash/alpha_bci_optim_grid.sh scripts/simulations/bci_optim.py WonRCP2RSVP preproc/won/all WonRCP2RSVP_ITR_GCB_Repr -1
```

All these results were moved into the folder `results/ITR_GCB_Repr/Optuna/<dset>/` to then be translated into CSV files.
