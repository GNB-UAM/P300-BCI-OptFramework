# README - Results formatting
[Return to table of contents](../../README.md).

## Formatting script
Simulations will generate at least one "\*.db" file, these are SQLite databases containing the optimization results.
These files are formatted into CSV files through `scripts/reports/optuna_bci_resfmt.py`.

Usage:
```
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/hoff/HoffStudy.db results/Optuna/OptimCVComplete/won/WonStudy.db -o results/Optuna/OptimCVComplete/CSV/AllResults.csv
```
This example joins two "\*.db" files—*HoffStudy.db* and *WonStudy.db* (-i results/...)—into a single CSV file named *AllResults.csv* (-o .../AllResults.csv) with the obtained results.
You can add as many input files as desired, they will be all concatenated within a CSV output file.

Additionally, we added a Bash script to remove cross-validation execution-time data—unnecesary for the analysis—from the "\*.db" files to decrease filesize.
**This is optional** and requires `sqlite3` command, example of usage:
```
sh scripts/reports/bash/drop_attrs.sh results/
```

## What we did
Before doing this, it is important to review what we did in the [simulation guidelines](../simulations/README.md).

### Format 32 electrodes results
- Hoffmann:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/hoff/HoffStudy.db -o results/Optuna/OptimCVComplete/CSV/HoffAll.csv
```

- Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/won/WonStudy.db -o results/Optuna/OptimCVComplete/CSV/WonAll.csv
```

- Stimulus-Level Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/wonrcp2rsvp/WonRCP2RSVPStudy.db -o results/Optuna/OptimCVComplete/CSV/WonRCP2RSVPAll.csv
```

### Format results for the rest of electrode setups
A CSV file was generated for each electrode set:
- Hoffmann:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/hoff/"HoffStudy.db" -o results/Optuna/electsets/CSV/HoffAll.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/hoff/"HoffStudy_ElectSet - hoff16.db" -o results/Optuna/electsets/CSV/Hoff16.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/hoff/"HoffStudy_ElectSet - hoff8.db" -o results/Optuna/electsets/CSV/Hoff8.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/hoff/"HoffStudy_ElectSet - hoff4.db" -o results/Optuna/electsets/CSV/Hoff4.csv
```

- Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/won/"WonStudy.db" -o results/Optuna/electsets/CSV/WonAll.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/won/"WonStudy_ElectSet - won16.db" -o results/Optuna/electsets/CSV/Won16.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/won/"WonStudy_ElectSet - won8.db" -o results/Optuna/electsets/CSV/Won8.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/won/"WonStudy_ElectSet - won4.db" -o results/Optuna/electsets/CSV/Won4.csv
```

- Stimulus-Level Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/OptimCVComplete/wonrcp2rsvp/"WonRCP2RSVPStudy.db" -o results/Optuna/electsets/CSV/WonRCP2RSVPAll.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/wonrcp2rsvp/"WonRCP2RSVPStudy_ElectSet - won16.db" -o results/Optuna/electsets/CSV/WonRCP2RSVP16.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/wonrcp2rsvp/"WonRCP2RSVPStudy_ElectSet - won8.db" -o results/Optuna/electsets/CSV/WonRCP2RSVP8.csv

python scripts/reports/optuna_bci_resfmt.py -i results/Optuna/electsets/wonrcp2rsvp/"WonRCP2RSVPStudy_ElectSet - won4.db" -o results/Optuna/electsets/CSV/WonRCP2RSVP4.csv
```

### Format results for ITR vs. GCB - Jensen–Shannon divergences analyses
- Hoffmann:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/ITR_GCB_Repr/Optuna/hoff/Hoff_ITR_GCB_Repr.db -o results/ITR_GCB_Repr/CSV/Hoff_ITR_GCB_Repr.csv
```

- Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/ITR_GCB_Repr/Optuna/won/Won_ITR_GCB_Repr.db -o results/ITR_GCB_Repr/CSV/Won_ITR_GCB_Repr.csv
```

- Stimulus-Level Won:
```sh
python scripts/reports/optuna_bci_resfmt.py -i results/ITR_GCB_Repr/Optuna/wonrcp2rsvp/WonRCP2RSVP_ITR_GCB_Repr.db -o results/ITR_GCB_Repr/CSV/WonRCP2RSVP_ITR_GCB_Repr.csv
```
