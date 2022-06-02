import argparse
import os
from bayes_opt import UtilityFunction
from utilities.json_io import load_coeff_bounds, write_suggestion
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json

parser = argparse.ArgumentParser()
parser.add_argument("-dir","--directory", help="directory for storing files", default = None)
parser.add_argument("-k","--kappa", help="specify directory for storing files", type=float, default = None)
parser.add_argument("-u","--utility_kind", help="specify directory for storing files", default = None)
parser.add_argument("-rs","--random_state", help="specify directory for storing files", default = None)

args = parser.parse_args()

def suggest(directory = None, 
            kappa = None, 
            utility_kind = None,
            random_state = None):
    
    # Set default arguments here, since argparse will overwrite anything in function definition with None if they are not included
    if directory is None: directory = os.getcwd()
    if kappa is None: kappa = 2.5
    if utility_kind is None: utility_kind = 'ucb'
    
    utility = UtilityFunction(kind=utility_kind, kappa=kappa, xi=0.0)
    coeff_bounds, file_coeff_bounds = load_coeff_bounds(directory)
       
    optimizer = BayesianOptimization(
        f=None,
        pbounds=coeff_bounds,
        verbose=2,
        random_state=7,
    )
    try: 
        load_logs(optimizer, logs=[os.path.join(directory,"history.json")]);
    except:
        print(f'Could not load history from {os.path.join(directory,"history.json")}.\nFile does not exist or the number of coefficients has changed. Suggesting without considering history.')
    suggestion = optimizer.suggest(utility)
    write_suggestion(directory = directory,
                     suggestion = suggestion)

if __name__ == '__main__':
    suggest(directory = args.directory,
            kappa = args.kappa,
            utility_kind = args.utility_kind,
            random_state = args.random_state)
    