import argparse
import os
from bayes_opt import UtilityFunction
from bayes_opt.event import Events
from utilities.json_io import load_suggestion, load_coeff_bounds, newJSONLogger
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json

#remove this after development
import random

parser = argparse.ArgumentParser()
parser.add_argument("-dir","--directory", help="directory for storing files", default = None)
parser.add_argument("score", help="score to add to the history", type=float)
args = parser.parse_args()

def register_score(score, directory = None):
    if directory is None: directory = os.getcwd()
    
    print(score)
    #Load suggested point
    suggestion, file_suggestion = load_suggestion(directory)
    print(suggestion)
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
    logger = newJSONLogger(path=os.path.join(directory,"history.json"))
    optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)
    
    #suggestion['a1'] = random.uniform(0.2, 0.8)
    optimizer.register(params=suggestion, target=score)


if __name__ == '__main__':
    register_score(score = args.score,
                   directory = args.directory)