import numpy as np
import os
import pandas as pd
from turborans.utilities.foam_automation.caserunner import run_until_convergence, get_endtime
from turborans.utilities.foam_automation.foamLossFunc import foamFieldLossFunc
from turborans.utilities.foam_automation.set_foam_coeff import set_foam_coef
from turborans.utilities.json_io import write_suggestion, write_json, load_coeff_default, load_coeff_bounds, load_history_loss_log, load_suggestion
from turborans.utilities.control import initialize
from turborans.bayes_io import suggest, register_score, summarize

import random

# Run simulation loop
foamdir = 'periodichills_running' # Main directory that the OpenFOAM simulations will be run in
savedir = 'periodichills_opt' # Directory for saving the best results

tunerdir = 'periodichills_tuner' # Directory for turbo-rans files
iterations=6 # For loop could also be changed to run until some sort of convergence or loss function tolerance
n_points_sampled = 4 # We sample 4 random points before beginning Bayesian optimization, this is optional
utility = 'poi' # Optimizer parameter
xi = 0.1 # Optimizer parameter
ref_df = pd.read_csv(os.path.join(tunerdir,'refdata.csv')) # See refdata.csv for file format, sparse or dense unstructured (x, y, z,...) field data


initialize(directory = tunerdir,
           coeff_bounds = None,
           coeff_default = None,
           restart = True) #Sets up turbo-rans files and clears past history if restart==True

foamLoss = foamFieldLossFunc(foamdir=foamdir,
                                    ref_df=ref_df,
                                    interp_method='nearest') #Convenient class for handling loss function computation using field data
np.random.seed(7)
a1_rand = np.random.uniform(.24, .6, size=(n_points_sampled)) #Initial random points
betaStar_rand = np.random.uniform(.045, .14, size=(n_points_sampled)) #Initial random points
score_best = 1E6 

for i in range(iterations):
    if i == 0: # First iteration uses default coefficients, so the suggestion is the default coefficient
        search_point=load_coeff_default(directory=tunerdir)
        write_suggestion(directory=tunerdir, suggestion=search_point)
    elif i < n_points_sampled: # Next iterations use random coefficients
        search_point = {"a1": a1_rand[i], "betaStar": betaStar_rand[i]}
        write_suggestion(directory=tunerdir, suggestion=search_point)
    else: # Coefficients for remaining iterations are suggested by the optimizer
        suggest(directory=tunerdir, random_state=7,utility_kind = utility, xi=xi)
    
    search_point = load_suggestion(directory=tunerdir)
    print(f'=====================================\nIteration: {i}\n=====================================')
    print(search_point)
    set_foam_coef(foamdir,search_point) # Writes the turbulence model coefficients to constant/turbulenceProperties
    last_time = run_until_convergence(case=foamdir, n_proc = 8) # PyFoam convergence runner
    score = -foamLoss.foam_gedcp(foamtime=last_time,
                                                   coef_default_dict = load_coeff_default(directory=tunerdir),
                                                   coef_dict=search_point,
                                                   error_calc_fields=['U','k'],
                                                   error_calc_intparams=[],
                                                   error_type = 'mse'
                                                  ) # Computes the GEDCP loss function, which combines error in U and error in k
                                                    # The foamLoss.foam_gedcp provides a convenient GEDCP loss function from OpenFOAM data
                                                   
    register_score(score=score, directory=tunerdir) # Register the loss function with the optimizer
    if abs(score) < abs(score_best): # If we have a new "optimal" case, copy it to the savedir
        score_best = score
        os.system(f'rm -r {savedir}')
        os.system(f'cp -r {foamdir} {savedir}')

summarize(directory='periodichills_tuner')
