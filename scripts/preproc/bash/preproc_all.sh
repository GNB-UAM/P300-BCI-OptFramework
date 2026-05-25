#!/bin/bash

# Check if the arguments are provided
if [ $# -lt 7 ]; then
    echo "Usage: $0 <preproc_script> <input_dir> <output_dir> <elect_set> <epoch_len> <sfreq> <dataset>";
    exit 1;
fi

# Set the directory containing the preprocessed data
preproc_script="$1";
data_dir="$2";
out_dir="$3";
elect_set="$4";
epoch_len="$5";
sfreq="$6";
dset="$7";

# List of subjects
if [[ "$dset" == "Hoffmann" ]]; then
    dsbl_sbjs=$(seq 1 4);
    ctrl_sbjs=$(seq 6 9);
    sbjs=($dsbl_sbjs $ctrl_sbjs);
elif [[ "$dset" == "Won" ]]; then
    sbjs=($(seq 1 55));
else
    echo "Unrecognised dataset";
    exit 1;
fi

# Loop through each subject
for sbj in "${sbjs[@]}"; do
    python "$preproc_script" -s "$sbj" -id "$data_dir" -od "$out_dir" -es "$elect_set" -el "$epoch_len" -sfreq "$sfreq";
    echo "Preproc done for subject $sbj at $out_dir";
done

