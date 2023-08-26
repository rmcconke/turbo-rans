from bayes_opt import UtilityFunction
from turborans.utilities.json_io import load_coeff_bounds, write_suggestion
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json
import logging
import os

def search_report(directory = os.getcwd(), 
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
