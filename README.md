# turbo-rans: straightforward & efficient optimization of turbulence model coefficients
![Airfoil](airfoil.png?raw=true "Airfoil")
# Overview
The core algorithm is:
1. `suggest` reads the history file, and tells you what coefficients to use
2. Run the simulation with these coefficients, and calculate the score
3. `register_score` updates the history file with the coefficients and corresponding score
4. Go back to Step 1.

## `suggest`
`suggest` recommmends coefficients based on one of three **suggestion modes**: 
1. `default_coefficients`: returns the default coefficients.
2. `sampling_parameters`: returns coefficients sampled from a Sobol sequence.
3. `bayesian_optimization`: performs Bayesian optimization and returns next query point. 

These modes are automatically detected based on the number of available data points (in other words, the current iteration). If `iter==0`, then the default coefficients are returns. If `iter<= n_samples`, then Sobol sampled coefficients are returned. Else, Bayesian optimization is used to suggest the next point.

## `register_score` 
`register_score` registers a given score and coefficient value with the Bayesian optimizer. Note that even if the suggestion didn't come from Bayesian optimization (the case for default and sampled coefficients), the score can and will still be registered with the optimizer. Depending on the optimizer mode, this registration may or may not trigger an update to a `history.json` file.

# Optimizer modes
An important choice is the global **optimizer mode**. There are two modes:
1. **JSON Mode** (`settings[json_mode] = True`): recommended for most use cases. In this mode, all necessary files are written and read at each iteration, so you can save progress and restart the optimization.
2. **Python Mode** (`settings[json_mode] = False`): designed for faster optimization problems where we don't need to stop and start the optimization. Use this for debugging simple optimization problems.

## Repo structure
Templates and examples for different use cases have been provided. These use cases are:
- **I have an OpenFOAM simulation that I want to optimize the coefficients for** -> see the `openfoam_periodichills` (field reference data) and airfoil `openfoam_airfoil`(integral parameter reference data) examples in the `examples` folder. Consider modifying these examples for your problem.
- **I have an Ansys Fluent simulation that I want to optimize the coefficients for** -> see the `fluent_cndv` (sparse wall measurements) example in the `examples` folder. This example modifies the GEKO coefficients within a journal file. This journal file sets the coefficients, runs the simulation, and exports the necessary wall quantities.
- **I want a CFD solver independent python script** -> see the `generic_python` template
- **I want a CFD solver independent shell script** -> see the `generic_shell` template

For the `templates`, you need to implement the "black box" function for your solver. This function should roughly: read the suggestion.json file, run a CFD simulation with these coefficients, compute the scoring function, and return the score. Design of the scoring function is critical and is discussed in detail in the associated reference. Note that a python implementation of the scoring function from the reference paper has been provided in `scoring_functions`.

The `examples` folder contains several examples and useful scripts for using the code with OpenFOAM and Ansys Fluent, and can be used as a guide to implementing your solver-specific black box function.

# Usage
The core optimizer is object-oriented, and is implemented in the `turborans/bayes_io.py` file. The usage of this object is flexibile. You can use it in the following ways:
1. **Python script I/O to the entire turbo-RANS library**: use the `suggest_coeffs.py`, `register_score.py`, and `summarize_search.py`, scripts in the main repository. The arguments to these scripts can be used to control the optimization. An example of this usage is coming soon. You can learn about the arguments using e.g. `python3 suggest_coeffs.py -h`
2. **Use the optimizer object within a single Python script**: see the examples, which utilize this approach.

More information about the utility function can be found at the core BayesianOptimization documentation: https://github.com/fmfn/BayesianOptimization.

**To use this code with your CFD solver, the only thing that needs to be implemented is calculation of the score function**. More information about the score function is given in the related paper. This code includes some examples in OpenFOAM and convenient solver-agnostic score functions in python, but we have left this open-ended to be more widely useful. The core `register_score` function does *not* rely on any particular CFD solver (though we have included some convenient examples for OpenFOAM and Ansys Fluent users).

## Required files for JSON mode:
**The only required file in JSON mode is `coefficients.json`**. 

At the start of optimization, the folder could look like:
```
turborans_directory
|- coefficients.json
|- settings.json (optional, include if you want different settings)
```

Then, after calling `suggest` for the first time:
```
tuner_directory
|- coefficients.json (unchanged)
|- settings.json (settings for the optimizer)
|- suggestion.json (next point to be probed)
|- mode.json (indicates suggestion mode used for suggestion.json)
```

After calling `register_score` with the first suggestion:
```
tuner_directory
|- coefficients.json (unchanged)
|- settings.json (settings for the optimizer)
|- suggestion.json (next point to be probed)
|- mode.json (indicates suggestion mode used)
|- history.json 
```

**At any point, you can update `settings.json` to modify the optimizer settings for the next suggestion. However, it is important to note that if `settings.json` exists, it will be used as the source of settings, NOT values in your script.**

Now, calling `suggest` again will read `coefficients.json` to determine the bounds, `settings.json` to determine the settings, and `history.json` to condition the optimizer object on past history. The next point will be stored in `suggestion.json`. This `suggest`->`register_score`->`suggest`->`register_score`->... loop continues until convergence. The user must specify the convergence condition here in your own code (e.g., number of iterations, or rchange in score.)

## Python mode:
Python mode does not require any files. Everything is done and stored within the optimizer object. This means that you can't stop and resume the optimization, if your script stops running. For this reason, JSON mode is usually recommended.




