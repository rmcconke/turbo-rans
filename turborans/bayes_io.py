#from ._suggest import suggest
#from ._register_score import register_score
from bayes_opt import UtilityFunction
#from turborans.utilities.json_io import load_coeff_bounds, write_suggestion
from bayes_opt import BayesianOptimization
from bayes_opt.util import load_logs
import json
import logging
import os
from bayes_opt import UtilityFunction, BayesianOptimization
from sklearn.gaussian_process.kernels import Matern
from scipy.stats import qmc
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from turborans.utilities.json_io import load_json, write_json, newJSONLogger, load_history_loss_log
from turborans.utilities.kernel import derive_length_scales, get_optimizer
from turborans.utilities.control import reset
from turborans.utilities.checks import validate_settings
#load_suggestion, load_coeff_file, load_coeff_bounds, newJSONLogger, load_history_loss_log
import json
import logging
import random
import os
import pandas as pd
import numpy as np


class optimizer():
    settings = {
                'force_restart': False,
                'start_with_defaults_if_given': True,
                'json_mode': False,
                'n_samples': 10,
                'random_state': None,
                'bo_utility_kind': 'ucb',
                'bo_kappa': 2.0,
                'bo_xi': 0.1,
                'kernel_relative_lengthscale': 0.1,
                'kernel_relative_lengthscale_bounds': [1E-2,1E1],
                'kernel_nu': 5/2
                }

    def __init__(self,
                 coeffs = None, 
                 turborans_directory=os.getcwd(), 
                 settings = 'default'):
        
        self.coeffs = coeffs
        self.directory = turborans_directory

        if os.path.exists(os.path.join(self.directory,"settings.json")):
            json_settings = load_json(self.directory, "settings.json")
            self.settings.update(json_settings)
        else:
            if settings != 'default':
                self.settings.update(settings)

        validate_settings(self)
        if self.settings['json_mode']:
            if self.coeffs == None:
                self.coeffs = load_json(self.directory, "coefficients.json")
            else:
                write_json(self.directory, self.coeffs, "coefficients.json")
            write_json(self.directory, self.settings, "settings.json")
            
        if 'default' in self.coeffs:
            self.default_coeffs_given = True
        else: 
            self.default_coeffs_given = False

        if self.settings['force_restart']: 
            reset(self.directory)

        self.utility = UtilityFunction(kind=self.settings['bo_utility_kind'],
                                       kappa=self.settings['bo_kappa'],
                                       xi=self.settings['bo_xi'])
        
        self.bayesian_optimizer = get_optimizer(coeff_bounds=self.coeffs['bounds'],
                                                relative_lengthscale=self.settings['kernel_relative_lengthscale'],
                                                relative_lengthscale_bounds=self.settings['kernel_relative_lengthscale_bounds'],
                                                nu=self.settings['kernel_nu'],
                                                random_state=self.settings['random_state']
                                                )
        self.infer_current_iteration()
        self.set_mode()
        self.samples_generated = False
        self.database_created = False

    def condition_bayesian_optimizer(self):
        if os.path.exists(os.path.join(self.directory,"history.json")):
            try: 
                load_logs(self.bayesian_optimizer, logs=[os.path.join(self.directory,"history.json")]);
            except:
                raise LookupError(f'Could not load history from {os.path.join(self.directory,"history.json")}, even though it exists.\nThe number of coefficients might have changed.')
        else:
            logging.info(f'No history file exists at {os.path.join(self.directory,"history.json")}, bayesian_optimizer is starting fresh')
    
    def infer_current_iteration(self):
        iter = len(self.bayesian_optimizer._space)
        self.iter = iter
        return iter
    
    def set_mode(self, mode = None):
        self.infer_current_iteration()
        if mode is None:
            if self.iter == 0:
                if self.default_coeffs_given and self.settings['start_with_defaults_if_given']:
                    self.mode = 'default_coefficient'
                else:
                    self.mode = 'sampling_parameters'
            elif self.iter <= self.settings['n_samples']:
                self.mode = 'sampling_parameters'
            else:
                self.mode = 'bayesian_optimization'
        else:
            self.mode = mode

    def generate_samples(self, n_samples):
        qrng = qmc.Sobol(d=len(self.coeffs['bounds'].keys()), seed=self.settings['random_state'])
        self.samples = qrng.random(n=2**(int(np.log2(n_samples))+1))
        for i,bounds in enumerate(self.coeffs['bounds'].values()):
            self.samples[:,i] = bounds[0] + self.samples[:,i]*(bounds[1]-bounds[0])
        self.samples_generated = True

    def _suggest_default(self):
        return self.coeffs['default']
           
    def _suggest_sample(self, index):
        if index >= len(self.samples):
            logging.info(f'Generating more samples, since index {index} is beyond len(samples) = {len(self.samples)}')
            self.generate_samples(len(self.samples)+1)
        suggestion = dict(zip(self.coeffs['bounds'].keys(), self.samples[index]))
        return suggestion

    def _suggest_bayesian_optimization(self):
        if self.iter < 5:
            raise ValueError("Bayesian optimizer should not be run without at least 5 initial samples")
        return self.bayesian_optimizer.suggest(self.utility)

    def suggest(self, mode = None):
        if self.settings['json_mode']:
            self._suggest_to_json(mode)
        else: 
            return self._suggest(mode)
        
    def _suggest_to_json(self, mode):
        self.condition_bayesian_optimizer()
        suggestion = self._suggest(mode)
        logging.info(f'Suggesting to json')
        write_json(self.directory, suggestion, "suggestion.json")
        write_json(self.directory, {"mode":self.mode}, "mode.json")
        
    def _suggest(self, mode):
        self.set_mode(mode)
        logging.info(f'Suggesting new value, current mode: {self.mode}')
        if self.mode == 'default_coefficient':
            return self._suggest_default()
        elif self.mode == 'sampling_parameters':
            if not self.samples_generated:
                self.generate_samples(self.settings['n_samples'])
            return self._suggest_sample(self.iter)
        else:
            return self._suggest_bayesian_optimization()

    def register_score(self, score, coefficients = None):
        if coefficients is None:
            if not self.settings['json_mode']:
                raise ValueError('You must provide a corresponding suggestion to be registered, unless turbo-RANS is in json_mode')
            else:
                suggestion = load_json(self.directory, "suggestion.json")
                self._register_score_json(score, suggestion)
        else:
            self._register_score(score, coefficients)
            self.update_database(score,coefficients)

    def _register_score_json(self, score, suggestion):
        if not os.path.exists(os.path.join(self.directory,"history.json")):
            logging.info(f'No history file exists at {os.path.join(self.directory,"history.json")}, creating and registering first point')
        logger = newJSONLogger(path=os.path.join(self.directory,"history.json"))
        self.bayesian_optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)
        logging.info(f'Registering score in {os.path.join(self.directory,"history.json")}')
        try:
            self._register_score(score, suggestion)
        except:
            # See issues associated with Bayesian Optimization library, sometimes optimizer attempts to probe duplicate point
            suggestion = {k: v+random.uniform(0.0000001, 0.000001) for k,v in suggestion.items()}
            logging.warning('Could not register score, maybe a duplicate point. Adding small random value to search point.')
            self._register_score(score, suggestion)
    
    def _register_score(self, score, suggestion):
        self.bayesian_optimizer.register(params=suggestion, target=score)

    def update_database(self, score, coefficients):
        if self.settings['json_mode'] is True:
            raise ValueError("update_database should only be used for non-json mode")

        if not self.database_created:
            self.database = {'iteration':[],'mode':[],'target':[]}
            [self.database.update({key: []}) for key in coefficients.keys()]
            self.database_created = True
        self.database['iteration'].append(self.iter)
        self.database['mode'].append(self.mode)
        [self.database[key].append(value) for key,value in coefficients.items()]
        self.database['target'].append(score)











