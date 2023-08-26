#from ._suggest import suggest
#from ._register_score import register_score
from bayes_opt import UtilityFunction
from turborans.utilities.json_io import load_coeff_bounds, write_suggestion
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json
import logging
import os
from bayes_opt import UtilityFunction, BayesianOptimization
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from turborans.utilities.json_io import load_suggestion, load_coeff_bounds, newJSONLogger
import json
import logging
import random
import os

def suggest(directory = os.getcwd(), 
            kappa: float = 2.0, 
            xi: float  = 0.1,
            utility_kind:str  = 'poi',
            random_state = None):
    '''
    Reads coef_bounds.json and history.json if it exists, suggests new search point, and saves suggestion to suggestion.json.

            Parameters:
                    directory (str): The tuner directory, containing "coef_bounds.json", "history.json". Default is os.getcwd().
                    kappa (float): kappa hyperparameter, applicable to ucb utility. Default is 2.0.
                    xi (float): xi hyperparameter, applicable to ei and poi utilities. Default is 0.1.
                    utility_kind: 'ucb', 'ei', or 'poi'. Default is 'poi'
                    random_state: optional random state.

            Returns:
                    None
    '''
    utility = UtilityFunction(kind=utility_kind, kappa=kappa, xi=xi)
    coeff_bounds = load_coeff_bounds(directory)
    
    if random_state is not None:
        optimizer = BayesianOptimization(
            f=None,
            pbounds=coeff_bounds,
            verbose=2,
            random_state=random_state,
        )
    else:
        optimizer = BayesianOptimization(
            f=None,
            pbounds=coeff_bounds,
            verbose=2,
        )
        
    if os.path.exists(os.path.join(directory,"history.json")):
        try: 
            load_logs(optimizer, logs=[os.path.join(directory,"history.json")]);
        except:
            raise LookupError(f'Could not load history from {os.path.join(directory,"history.json")}, even though it exists.\nThe number of coefficients might have changed.')
    
    else:
        logging.info(f'No history file exists at {os.path.join(directory,"history.json")}, suggesting without considering history ')
    suggestion = optimizer.suggest(utility)
    write_suggestion(directory = directory,
                     suggestion = suggestion)
    return

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