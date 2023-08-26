#!/bin/bash
export PYTHONPATH=../../

./reset_example.sh
python3 periodichills_turbo.py | tee example.log
