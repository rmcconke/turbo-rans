import argparse
import os
from bayes_opt import UtilityFunction
from bayes_opt.event import Events
from utilities.json_io import load_suggestion, load_coeff_bounds, newJSONLogger
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json
import logging
import random

def register_score(score: float, directory = os.getcwd()):
    '''
    Registers the score and corresponding search point within the history file. If no history file exists, creates a new one.

            Parameters:
                    score (float): The score value associated with the current "suggestion.json".
                    directory (str): The tuner directory, containing "history.json", suggestion.json". Default is os.getcwd().

            Returns:
                    None
    '''
    suggestion = load_suggestion(directory)
    coeff_bounds = load_coeff_bounds(directory)

    optimizer = BayesianOptimization(
        f=None,
        pbounds=coeff_bounds,
        verbose=2,
        random_state=0,
    )
    
    if os.path.exists(os.path.join(directory,"history.json")):
        try: 
            load_logs(optimizer, logs=[os.path.join(directory,"history.json")]);
        except:
            raise LookupError(f'Could not load history from {os.path.join(directory,"history.json")}.\nThe number of coefficients might have changed.')
    else:
        logging.info(f'No history file exists at {os.path.join(directory,"history.json")}, creating and registering first point')
        
    logger = newJSONLogger(path=os.path.join(directory,"history.json"))
    optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)
    logging.info(f'Registering score in {os.path.join(directory,"history.json")}')
    
    try:
        optimizer.register(params=suggestion, target=score)
    except:
        # See issues associated with Bayesian Optimization library, sometimes optimizer attempts to probe duplicate point
        suggestion = {k: v+random.uniform(0.0000001, 0.000001) for k,v in suggestion.items()}
        logging.warning('Could not register score, maybe a duplicate point. Adding small random value to search point.')
        optimizer.register(params=suggestion, target=score)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir","--directory", help="directory for storing files", default = os.getcwd())
    parser.add_argument("score", help="score to add to the history", type=float)
    parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")
    args = parser.parse_args()
    register_score(score = args.score,
                   directory = args.directory)
