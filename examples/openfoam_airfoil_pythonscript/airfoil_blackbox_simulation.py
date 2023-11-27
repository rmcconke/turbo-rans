import numpy as np
import os
import pandas as pd
from turborans.utilities.foam_automation.caserunner import run_until_convergence
from turborans.utilities.foam_automation.set_foam_coeff import set_foam_coef
from turborans.utilities.json_io import load_json
from turborans.objective_functions.GEDCP import gedcp
import argparse

cl_ref = 1.0707

def read_force_coefficient(foamdir,coef_name):
    df = pd.read_csv(os.path.join(foamdir,'postProcessing/forceCoeffs1/0/coefficient_0.dat'),delimiter ='\t',skiprows = 12)
    df.columns = df.columns.str.replace(' ', '')
    return float(df[coef_name].iloc[-1])

def blackbox_simulation(foamdir, tunerdir):
    search_point = load_json(tunerdir, "suggestion.json")
    coeffs = load_json(tunerdir, "coefficients.json")
    print(f'blackbox_simulation running airfoil simulation with coefficients: {search_point}')
    set_foam_coef(foamdir, search_point) # Writes the turbulence model coefficients to constant/turbulenceProperties
    run_until_convergence(case=foamdir, n_proc = 8) # PyFoam convergence runner
    cl_sim = read_force_coefficient(foamdir, 'Cl')
    score = gedcp(integral_param_sim_dict = {'Cl': cl_sim},
    			  integral_param_ref_dict = {'Cl': cl_ref},
                  coef_default_dict=coeffs['default'],
                  coef_dict=search_point)
    print(f'blackbox_simulation got Cl_sim: {cl_sim}, GEDCP score: {score}')
    return score

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("foam_directory", default = os.path.join(os.getcwd(),'airfoil_running'))
    parser.add_argument("tuner_directory", default = os.path.join(os.getcwd(),'airfoil_tuner'))
    args = parser.parse_args()
    print(blackbox_simulation(args.foam_directory, args.tuner_directory))
    
