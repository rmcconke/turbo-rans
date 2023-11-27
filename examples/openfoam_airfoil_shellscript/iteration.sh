#!/bin/bash
export PYTHONPATH=../../

python3 -u ../../suggest_coeffs.py -dir airfoil_tuner -rs 7
score=$(python3 -u airfoil_blackbox_simulation.py airfoil_running airfoil_tuner)
echo $score
python3 -u ../../register_score.py $score -dir airfoil_tuner

