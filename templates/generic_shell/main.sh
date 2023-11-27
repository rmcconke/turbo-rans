#!/bin/bash
export PYTHONPATH=../../

for i in {0..20};
do
	echo Iteration $i
	python3 -u ../../suggest_coeffs.py #Optional fix random seed with e.g: -rs 7
	score=`/bin/bash blackbox_simulation.sh`
	echo $score
	python3 -u ../../register_score.py $score 
done

python3 ../../summarize_search.py .
