#!/bin/bash
export PYTHONPATH=../../

./reset.sh
cp -r airfoil_template airfoil_running

for i in {0..9};
do
	echo Iteration $i
	./iteration.sh
done

python3 ../../summarize_search.py airfoil_tuner
