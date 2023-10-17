import numpy as np
import os
import pandas as pd
from turborans.utilities.foam_automation.caserunner import run_until_convergence, get_endtime
from turborans.utilities.foam_automation.foamLossFunc import foamFieldLossFunc
from turborans.utilities.foam_automation.set_foam_coeff import set_foam_coef
from turborans.utilities.analysis import summarize

from turborans.bayes_io import optimizer

# Run simulation loop
foamdir = 'periodichills_running' # Main directory that the OpenFOAM simulations will be run in
savedir = 'periodichills_opt' # Directory for saving the best results

tunerdir = 'periodichills_tuner' # Directory for turbo-rans files

iterations = 10 # For loop could also be changed to run until some sort of convergence or loss function tolerance

ref_df = pd.read_csv(os.path.join(tunerdir,'refdata.csv')) # See refdata.csv for file format, sparse or dense unstructured (x, y, z,...) field data

foamLoss = foamFieldLossFunc(foamdir=foamdir,
                                    ref_df=ref_df,
                                    interp_method='nearest') #Convenient class for handling loss function computation using field data
np.random.seed(7)
score_best = 1E6 

turborans = optimizer(coeffs= {'default': {
                                            'a1': 0.31,
                                            'betaStar': 0.09
                                           },
                               'bounds': {
                                            'a1': [0.24, 0.6],
                                            'betaStar': [0.045,0.14],
                                            }},
                        turborans_directory = tunerdir,
                        settings= {'force_restart': True,
                                   'random_state': 7,
                                   'n_samples': 5})

for i in range(iterations):
    print(f'=====================================\nIteration: {i}\n=====================================')
    search_point = turborans.suggest()
    print(f'Mode: {turborans.mode}')
    print(search_point)
    set_foam_coef(foamdir,search_point) # Writes the turbulence model coefficients to constant/turbulenceProperties
    last_time = run_until_convergence(case=foamdir, n_proc = 8) # PyFoam convergence runner
    score = -foamLoss.foam_gedcp(foamtime=last_time,
                                                   coef_default_dict = turborans.coeffs['default'],
                                                   coef_dict=search_point,
                                                   error_calc_fields=['U','k'],
                                                   error_calc_intparams=[],
                                                   error_type = 'mse'
                                                  ) # Computes the GEDCP loss function, which combines error in U and error in k
                                                    # The foamLoss.foam_gedcp provides a convenient GEDCP loss function from OpenFOAM data
    
    turborans.register_score(score=score, coefficients=search_point)
                        
    if abs(score) < abs(score_best): # If we have a new "optimal" case, copy it to the savedir
        score_best = score
        os.system(f'rm -r {savedir}')
        os.system(f'cp -r {foamdir} {savedir}')

summarize(turborans)
