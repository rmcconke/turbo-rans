# rans_tuner - straightforward & efficient optimization of turbulence model coefficients

# Overview
The core algorithm is made up of repeated calls to `suggest` and `register_score`. `suggest` takes a *mandatory* `coeff_bounds.json`, looks for an *optional* `history.json` (to consider previous evaluations), and then saves a `suggestion.json` file. Then, once the score function is known, `register_score` takes a *mandatory* score value, reads the `suggestion.json` file, and saves a `history.json` file that can be read by `BayesianOptimization`.


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

# Usage
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

**To use this code with your CFD solver, the only thing that needs to be implemented is calculation of the score function**. More information about the score function is given in the related paper. This code includes some examples in OpenFOAM and convenient solver-agnostic score functions in python, but we have left this open-ended to be more widely useful. We have *not* coupled the core `register_score` function tightly with an OpenFOAM-based score calculation function (though we have included some convenient scripts for OpenFOAM users).


# Examples
The `examples` folder contains several examples and useful scripts for using the code with OpenFOAM. The `templates` folder contains a template python script that is only missing the score function implementation (which is CFD solver specific). `templates` also includes a shell script example, with a simple black-box score function that could be replaced by a CFD solving and score calculation script.



