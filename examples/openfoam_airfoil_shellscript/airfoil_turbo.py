import numpy as np
import os
import pandas as pd
from turborans.utilities.foam_automation.caserunner import run_until_convergence, get_endtime
from turborans.utilities.foam_automation.set_foam_coeff import set_foam_coef
from turborans.utilities.analysis import summarize
from turborans.utilities.json_io import load_json
from turborans.objective_functions.GEDCP import gedcp
from turborans.bayes_io import optimizer
from airfoil_blackbox_simulation import blackbox_simulation



# Run simulation loop
foamdir = 'airfoil_running' # Main directory that the OpenFOAM simulations will be run in
savedir = 'airfoil_opt' # Directory for saving the best results

tunerdir = 'airfoil_tuner' # Directory for turbo-rans files

iterations = 10 # For loop could also be changed to run until some sort of convergence or loss function tolerance

cl_ref = 1.0707

                                    
np.random.seed(7)
score_best = 1E6 

turborans = optimizer(turborans_directory = tunerdir,
                      settings= {'force_restart': False,
                                 'random_state': 7,
                                 'n_samples': 5})

coeffs = load_json(tunerdir,'coefficients.json')

for i in range(iterations):
    print(f'=====================================\nIteration: {i}\n=====================================')
    turborans.suggest()
    print(f'turbo-RANS suggestion mode: {turborans.mode}')
    score = blackbox_simulation(foamdir, tunerdir)    
    turborans.register_score(score=score)          
    
    if abs(score) < abs(score_best): # If we have a new "optimal" case, copy it to the savedir
        score_best = score
        os.system(f'rm -r {savedir}')
        os.system(f'cp -r {foamdir} {savedir}')

summarize(turborans)
