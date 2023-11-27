In this airfoil example, turbo-RANS is run in JSON mode within a shell script.
At the start of the optimization, only `coefficients.json` within `airfoil_tuner` is required.
The suggest-register loop is implemented in the `iteration.sh` script. 
You can call this script in a loop (e.g. `airfoil_example.sh`) until optimization is completed.
