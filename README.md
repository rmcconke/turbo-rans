# turbo-rans: straightforward & efficient optimization of turbulence model coefficients
![Airfoil](airfoil.png?raw=true "Airfoil")
# Overview
The core algorithm is:
1. `suggest` reads the history file, and tells you what coefficients to use
2. Run the simulation with these coefficients, and calculate the score
3. `register_score` updates the history file with the coefficients and corresponding score
4. Go back to Step 1.

## Repo structure
Templates and examples for different use cases have been provided. These use cases are:
- **I have an OpenFOAM simulation that I want to optimize the coefficients for** -> see the periodic hills (field reference data) and airfoil (integral parameter reference data) `examples`, and the `OpenFOAM` template. Consider modifying the examples for your problem.
- **I want a CFD solver independent python script** -> see the `generic_python` template
- **I want a CFD solver independent shell script** -> see the `generic_shell` template

For the `templates`, you need to implement the "black box" function for your solver. This function should roughly: read the suggestion.json file, run a CFD simulation with these coefficients, compute the scoring function, and return the score. Design of the scoring function is critical and is discussed in detail in the associated reference. Note that a python implementation of the scoring function from the reference paper has been provided in `scoring_functions`.

The `examples` folder contains several examples and useful scripts for using the code with OpenFOAM, and can be used as a guide to implementing your solver-specific black box function.

# Usage
`suggest` takes a *mandatory* `coeff_bounds.json`, looks for an *optional* `history.json` (to consider previous evaluations), and then saves a `suggestion.json` file. Then, once the score function is known, `register_score` takes a *mandatory* score value, reads the `suggestion.json` file, and saves a `history.json` file that can be read by `BayesianOptimization`.

This code is intended to be *CFD solver agnostic*. The two core functions, `suggest` and `register_score`, can be accessed through calling `suggest_coeffs.py` and `update_history.py` as python scripts with required arguments. You can learn about the arguments using `python3 suggest_coeffs.py -h`:

```
usage: suggest_coeffs.py [-h] [-dir DIRECTORY] [-k KAPPA] [-xi XI]
                         [-u UTILITY_KIND] [-rs RANDOM_STATE] [-f FFF]

options:
  -h, --help            show this help message and exit
  -dir DIRECTORY, --directory DIRECTORY
                        directory for storing files
  -k KAPPA, --kappa KAPPA
                        kappa parameter for utility function UCB. Higher
                        values (e.g. 10) prefer exploration, lower values
                        (e.g. 1) prefer exploitation.
  -xi XI, --xi XI       xi parameter for utility functions EI and POI. Higher
                        values (e.g. 0.1) prefer exploration, lower values
                        (e.g. 1E-4) prefer exploitation.
  -u UTILITY_KIND, --utility_kind UTILITY_KIND
                        utility function kind, UCB/EI/POI.
  -rs RANDOM_STATE, --random_state RANDOM_STATE
                        random state for optimizer.
```

Note that `suggest_coeffs.py` has *no required arguments*. This is because it only needs to load the mandatory `coeff_bounds.json` file, search for `history.json` that exists, and then save a suggestion.

```
usage: update_history.py [-h] [-dir DIRECTORY] [-f FFF] score

positional arguments:
  score                 score to add to the history

options:
  -h, --help            show this help message and exit
  -dir DIRECTORY, --directory DIRECTORY
                        directory for storing files
```
Note that `update_history.py` has *one required argument:* `score`. This script assumes that `score` corresponds to the current `suggestion.json` file.

More information about the utility function can be found at the core BayesianOptimization documentation: https://github.com/fmfn/BayesianOptimization.

**To use this code with your CFD solver, the only thing that needs to be implemented is calculation of the score function**. More information about the score function is given in the related paper. This code includes some examples in OpenFOAM and convenient solver-agnostic score functions in python, but we have left this open-ended to be more widely useful. The core `register_score` function does *not* rely on any particular CFD solver (though we have included some convenient scripts for OpenFOAM users).

## Directory structure explained
The core files are:
```
tuner_directory
|- coeff_bounds.json (mandatory always)
|- suggestion.json
|- history.json
```

At the start of optimization, the folder could look like:
```
tuner_directory
|- coeff_bounds.json (mandatory always)
```

Then, after calling `suggest` for the first time:
```
tuner_directory
|- coeff_bounds.json (mandatory always)
|- suggestion.json
```

After calling `register_score` with the first suggestion:
```
tuner_directory
|- coeff_bounds.json (mandatory always)
|- suggestion.json
|- history.json
```

Now that `history.json` exists, `suggest` will read this file before suggesting another point, in order to take past evaluations into consideration.





