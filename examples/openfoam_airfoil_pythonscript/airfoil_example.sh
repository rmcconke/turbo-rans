#!/bin/bash
export PYTHONPATH=../../

./reset.sh
cp -r airfoil_template airfoil_running

# First call 
python3 -u airfoil_turbo.py | tee example.log

# Second call will continue optimization where it left off
#python3 -u airfoil_turbo.py | tee example.log

