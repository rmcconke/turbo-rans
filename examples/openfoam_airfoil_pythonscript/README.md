In this airfoil example, turbo-RANS is run in JSON mode within a python script.
At the start of the optimization, only `coefficients.json` within `airfoil_tuner` is required.
The first time `airfoil_turbo.py` is run, it will run 10 iterations (1 default, 5 samples, remainder BO).
Subsequently calling the `airfoil_turbo.py` python script will continue the optimization, using BO (since sufficient samples are available).
