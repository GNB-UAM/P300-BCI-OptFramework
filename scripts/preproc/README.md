# README - Preprocessing
[Return to table of contents](../../README.md).

## Hoffmann preprocessing
Hoffmann et al. dataset was preprocessed with the script `scripts/preproc/preproc_script_hoff.py`, which applies (in this order):
1. Mastoids averaging reference subtraction.
2. 6th order Forward-Backward Butterworth Filter 1-12Hz.
3. Downsampling from 2048Hz to 32Hz.
4. One second epochs extraction from stimulus onset.
5. Electrodes selection.
6. Trial trimming to the first 20 to homogenize runs.

Usage example:
```
python scripts/preproc/preproc_script_hoff.py -s 1 -id data/hoffmann_efficient_2008/OriginalDataEPFL -od preproc/S1 -el 1 -sfreq 32 -es "All"
```
In this example, EEG time series from the first subject (`-s 1`) are preprocessed with an epoch length of one second (`-el 1`) and downsampled to 32Hz (-sfreq 32) using all electrodes (`-es "All"`).

We also provide a Bash script to preprocess signals from all subjects and electrode setups automatically: `scripts/preproc/bash/preproc_all.sh`.
Parameters must be provided in this order: `./scripts/preproc/bash/preproc_all.sh <preproc_script> <input_dir> <output_dir> <elect_set> <epoch_len> <sfreq> <dataset>`

Usage example:
```
sh scripts/preproc/bash/preproc_all.sh scripts/preproc/preproc_script_hoff.py data/hoffmann_efficient_2008/OriginalDataEPFL preproc/hoff/"Hoffmann 4 set" "Hoffmann 4 set" 1 32 Hoffmann
```

## Won preprocessing
Won et al. dataset was preprocessed with the script `scripts/preproc/preproc_script_won.py`, which applies (in this order):
1. Common average reference subtraction.
2. 4th order Forward-Backward Butterworth Filter 0.5-10Hz.
3. 600 milisecond epochs extraction from stimulus onset.
4. Baseline correction with 200 miliseconds before the stimulus onset.
5. Downsampling from 512 to 20Hz by averaging 24-time points without overlapping.
5. Electrodes selection.
6. Run trimming to the first 5 to homogenize sessions.

Usage example:
```
python scripts/preproc/preproc_script_won.py -s 1 -id data/won_eeg_2022/OriginalDataWon -od preproc/won -el .6 -sfreq 20 -es All
```
In this example, EEG time series from the first subject (`-s 1`) are preprocessed with an epoch length of 600 miliseconds (`-el .6`) and downsampled to 20Hz (-sfreq 20) using all electrodes (`-es "All"`).

We also provide a Bash script to preprocess signals from all subjects and electrode setups automatically: `scripts/preproc/bash/preproc_all.sh`.
Parameters must be provided in this order: `./scripts/preproc/bash/preproc_all.sh <preproc_script> <input_dir> <output_dir> <elect_set> <epoch_len> <sfreq> <dataset>`

Usage example:
```
sh scripts/preproc/preproc_all.sh scripts/preproc/preproc_script_won.py data/won_eeg_2022/OriginalDataWon preproc/won/all "All" .6 20 Won
```

## What we did
We executed the automatic Bash script for every electrode subset and saved outputs within the `preproc` folder at the root directory:

First for Hoffmann et al:
```sh
x=("Hoffmann 16 set" "Hoffmann 8 set" "Hoffmann 4 set" "All");
for i in $x; do
    sh scripts/Preprocessing/preproc_all.sh scripts/Preprocessing/preproc_script_hoff.py data/hoffmann_efficient_2008/OriginalDataEPFL preproc/hoff/"$i" "$i" 1 32 Hoffmann;
    echo "Finished '$i'";
done;
```
After doing this, every preprocessing folder was renamed into `("hoff16" "hoff8" "hoff4" "all")`, respectively.

Lastly for Won et al:
```sh
y=("Won 16 set" "Won 8 set" "Won 4 set" "All");
for i in $y; do
    sh scripts/Preprocessing/preproc_all.sh scripts/Preprocessing/preproc_script_won.py data/won_eeg_2022/OriginalDataWon preproc/won/"$i" "$i" .6 20 Won;
    echo "Finished '$i'";
done;
```
After doing this, every preprocessing folder was renamed into `("won16" "won8" "won4" "all")`, respectively.
