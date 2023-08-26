#!/bin/bash
# Note: requires jq (json parser)
# To reset the optimization, delete history.json and suggestion.json
#export PYTHONPATH=../../

for i in {0..10}
do 
    echo "===== Iteration: $i ====="
    python3 ../../suggest_coeffs.py
    score=`/bin/bash blackbox_simulation.sh`
    python3 ../../update_history.py $score
done