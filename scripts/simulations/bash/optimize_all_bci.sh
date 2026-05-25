#!/bin/bash

# Check if the arguments are provided
if [ $# -lt 5 ]; then
    echo "Usage: $0 <optim_script> <dataset> <input_dir> <output_db> <n_jobs>";
    exit 1;
fi

optim_script="$1";
dset="$2";
data_dir="$3";
outdb="$4";
njobs="$5";

N_TRIALS=16

# List of subjects
if [[ "$dset" == "Hoffmann" ]]; then
    sbjs=(1 2 3 4 6 7 8 9);
elif [[ "$dset" == "Won" || "$dset" == "WonRCP2RSVP" ]]; then
    sbjs=($(seq 1 55));
else
    echo "Unrecognised dataset";
    exit 1;
fi

# Optimization Strategies
optim_strats=("ITR" "¾Gain + ¼Cons" "½Gain + ½Cons" "¼Gain + ¾Cons");

# ERP Detectors & Scalers
scalers=(0 0 1);
erp_dets=("LinearDiscriminantAnalysis" "RandomForestClassifier" "LinearSVC");

# Loop through each subject
for sbj in "${sbjs[@]}"; do
    echo "=================== Subject $sbj started ===================";
    for ((erpd_idx=0; erpd_idx<${#erp_dets[@]}; erpd_idx++)); do
        echo -e "\t \t =================== ERPd ${erp_dets[$erpd_idx]} started ===================";
        if [[ "${scalers[$erpd_idx]}" -eq 1 ]]; then
            python "$optim_script" -d "$dset" -s "$sbj" -id "$data_dir" -o "$outdb" -os "${optim_strats[@]}" -std -erpd "${erp_dets[$erpd_idx]}" -j "$njobs" -t "$N_TRIALS";
        else
            python "$optim_script" -d "$dset" -s "$sbj" -id "$data_dir" -o "$outdb" -os "${optim_strats[@]}" -erpd "${erp_dets[$erpd_idx]}" -j "$njobs" -t "$N_TRIALS";
        fi
        echo -e "\t \t =================== ERPd ${erp_dets[$erpd_idx]} done ===================";
    done
    echo "=================== Subject $sbj done ===================";
done
