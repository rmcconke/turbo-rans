#!/bin/bash
export PYTHONPATH=../../

./reset_example.sh
cp -r periodichills_template periodichills_running
# Optionally move tuner directory outside of running directory
mv periodichills_running/periodichills_tuner periodichills_tuner
rm -r periodichills_running/tuner
python3 periodichills_turbo.py | tee example.log
