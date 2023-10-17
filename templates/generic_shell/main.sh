#!/bin/bash
# Note: requires jq (json parser)
# To reset the optimization, delete history.json and suggestion.json
#export PYTHONPATH=../../

for i in {0..19}
do 
    echo "===== Iteration: $i ====="
    python3 ../../suggest_coeffs.py
    cat mode.json
    score=`/bin/bash blackbox_simulation.sh`
    python3 ../../update_history.py $score
done

python3 ../../summarize_search.py .
