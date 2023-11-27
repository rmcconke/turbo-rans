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
    """ Main turbo-RANS optimizer object.
    This optimizer object is designed to be the primary I/O for turbo-RANS. The json_mode setting is important; it indicates
    a global mode for this object. If this object is acting in json_mode = False, then it is designed to not save progress
    and simply run within a single python script. json_mode = True is recommended for the majority of applications, where
    saving progress is important. 
    

    Attributes
    ----------
    settings : dict
        a dictionary of settings for the optimizer.
        settings and current defaults:
                'force_restart': False,
                'start_with_defaults_if_given': True,
                'json_mode': True,
                'n_samples': 10,
                'random_state': None,
                'bo_utility_kind': 'ucb',
                'bo_kappa': 2.0,
                'bo_xi': 0.1,
                'kernel_relative_lengthscale': 0.1,
                'kernel_relative_lengthscale_bounds': [1E-2,1E1],
                'kernel_nu': 5/2

    coeffs : dict
        coefficient dictionary
    directory : str
        location for any file I/O
    default_coeffs_given : boolean
        flag to indicate whether or not default coefficients are provided in coeffs
    bayesian_optimizer : bayesian_optimization library object
    mode : str
        current mode for next recommendation, 'default_coefficient', 'sampling_paramerers', or 'bayesian_optimization'
    iter : int
        current optimization iteration number, equal to number of points in history
    samples : array
        sobol-sequence generated samples
    samples_generated: boolean
        flag to indicate whether sobol samples have been generated
    database : dict
        valid only for json_mode: False, dictionary containing information for summary at end of optimization
    database_created : boolean
        flag to indicate whether database has been generated
    
    Methods
    -------
    suggest(mode = None)
        gives the next suggestion. Mode is inferred if mode == None. If you attempt to set mode to bayesian_optimization with,
        insufficient points available, an error will be thrown.
    register_score(score, coefficients = None)
        registers the score with the underlying bayesian_optimization object. If coefficients = None, the coefficients in suggestion.json 
        are used as the coefficients. This means that in non-json mode, the coefficients argument must be provided.
    """
    settings = {
                'force_restart': False,
                'start_with_defaults_if_given': True,
                'json_mode': True,
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
        """
        Parameters
        ----------
        coeffs : dict, optional
            coefficient dictionary, containing bounds and defaults. e.g.
            {
                "default": {
                    "x": -0.5,
                    "y": 2
                },
                "bounds": {
                    "x": [
                        -1,
                        1
                    ],
                    "y": [
                        -10,
                        10
                    ]
                }
            }
            If coeffs is not given or coeffs = None, the coefficients are read from coefficients.json (this required json_mode = True). 
            coeffs can be specified in either json_mode = True or False. The coefficients.json file will only be read
            if coeffs = None, and json_mode = True.
        turborans_directory : str, optional
            directory for file I/O. If not given, the current directory will be used.
        
        settings : str or dict, optional
            if not given, or equal to 'default', default settings will be used. If you wish to change the settings, you must supply a dict
            with the settings that should be changed. If a settings.json file exists in the directory, this argument will be ignored.
            Default settings:
                    {
                        'force_restart': False,
                        'start_with_defaults_if_given': True,
                        'json_mode': True,
                        'n_samples': 10,
                        'random_state': None,
                        'bo_utility_kind': 'ucb',
                        'bo_kappa': 2.0,
                        'bo_xi': 0.1,
                        'kernel_relative_lengthscale': 0.1,
                        'kernel_relative_lengthscale_bounds': [1E-2,1E1],
                        'kernel_nu': 5/2
                    }
        """
        
        self.coeffs = coeffs
        self.directory = turborans_directory

        # Attempt to find settings.json file. If not found, update any non-default settings supplied in the init argument.
        if os.path.exists(os.path.join(self.directory,"settings.json")):
            json_settings = load_json(self.directory, "settings.json")
            self.settings.update(json_settings)
        else:
            if settings != 'default':
                self.settings.update(settings)

        # Check if settings are valid.
        validate_settings(self)

        # If we're in json_mode, look for coefficients.json if coeffs are not provided in init argument.
        # If they are provided, write them to a json file.
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

        # Reset optimizier if force_restart is True.
        if self.settings['force_restart']: 
            reset(self.directory)

        # Get bayesian_optimizer and utility based on current settings.
        if not self.settings['json_mode']:
            self._get_bayesian_optimizer()
                    
        self.samples_generated = False
        self.database_created = False

    def _condition_bayesian_optimizer(self):
        """Conditions the bayesian optimizer on history.json if we're in json_mode."""
        if os.path.exists(os.path.join(self.directory,"history.json")):
            try: 
                load_logs(self.bayesian_optimizer, logs=[os.path.join(self.directory,"history.json")]);
            except:
                raise LookupError(f'Could not load history from {os.path.join(self.directory,"history.json")}, even though it exists.\nThe number of coefficients might have changed.')
        else:
            # If no history file exists, we assume that this is the first iteration.
            logging.info(f'No history file exists at {os.path.join(self.directory,"history.json")}, assumed to be starting fresh')
    
    def _infer_current_iteration(self):
        """Infer the current iteration number based on the number of registered points."""
        iter = len(self.bayesian_optimizer._space)
        self.iter = iter
        return iter
    
    def _set_mode(self, mode = None):
        """Set the optimizer mode based on iteration number."""
        self._infer_current_iteration()
        if mode is None:
            if self.iter == 0:
                # If it is the first iteration, either suggest defaults (if they are given) or suggest the first sampled point.
                if self.default_coeffs_given and self.settings['start_with_defaults_if_given']:
                    self.mode = 'default_coefficient'
                else:
                    self.mode = 'sampling_parameters'
            elif self.iter <= self.settings['n_samples']:
                self.mode = 'sampling_parameters'
            else:
                self.mode = 'bayesian_optimization'
        else:
            # If we manually set the mode, we don't try to infer it.
            self.mode = mode

    def _generate_samples(self, n_samples):
        """ Generated sobol-sequence samples for each coefficient."""
        qrng = qmc.Sobol(d=len(self.coeffs['bounds'].keys()), seed=self.settings['random_state'])
        self.samples = qrng.random(n=2**(int(np.log2(n_samples))+1))
        for i,bounds in enumerate(self.coeffs['bounds'].values()):
            self.samples[:,i] = bounds[0] + self.samples[:,i]*(bounds[1]-bounds[0])
        self.samples_generated = True

    def _suggest_default(self):
        """ Returns the default coefficients provided."""
        return self.coeffs['default']
           
    def _suggest_sample(self, index):
        """ Returns a sobol-sequence sample for each coefficient"""

        # In some cases, we might ask for more samples than initially generated, so we need to generate an additional one
        if index >= len(self.samples):
            logging.info(f'Generating more samples, since index {index} is beyond len(samples) = {len(self.samples)}')
            self._generate_samples(len(self.samples)+1)
        
        # Convert the samples array into a dict of coefficient suggestions
        suggestion = dict(zip(self.coeffs['bounds'].keys(), self.samples[index]))
        return suggestion

    def _suggest_bayesian_optimization(self):
        """ Suggests a point using the bayesian optimizer."""

        if self.iter < 5: 
            # Strange behavior can occur when the bayesian optimizer has too few initial samples are available.
            raise ValueError("Bayesian optimizer should not be run without at least 5 initial samples")

        self.utility = UtilityFunction(kind=self.settings['bo_utility_kind'],
                                            kappa=self.settings['bo_kappa'],
                                            xi=self.settings['bo_xi'])
        
        return self.bayesian_optimizer.suggest(self.utility)

    def suggest(self, mode = None):
        """ Primary suggestion I/O method. Suggests the next coefficient. When mode = None,automatically determines appropriate mode. Writes to suggestion.json if in json_mode. If json_mode is False, then returns the suggestion as a dict."""
        if self.settings['json_mode']:
            return self._suggest_to_json(mode)
        else: 
            return self._suggest(mode)
        
    def _suggest_to_json(self, mode):
        """ Writes suggestion to suggestion.json."""

        # Condition bayesian optimizer object with all available points
        self._get_bayesian_optimizer()

        # Gets the suggestion as a dict
        suggestion = self._suggest(mode)

        # Write dict to json
        logging.info(f'Suggesting to json')
        write_json(self.directory, suggestion, "suggestion.json")
        write_json(self.directory, {"mode":self.mode}, "mode.json")
        return suggestion
        
    def _suggest(self, mode):
        """ Core suggestion method.
        mode is usually None, and then self.mode will be inferred in self._set_mode(None). After inferring the mode, then the suggestion
        made will depend on the mode ('default_coefficient', 'sampling_parameters', or 'bayesian_optimization')
        """
        self._set_mode(mode)
        logging.info(f'Suggesting new value, current mode: {self.mode}')

        # Default coefficient suggestion
        if self.mode == 'default_coefficient':
            return self._suggest_default()
        
        # Sampling parameters suggestion
        elif self.mode == 'sampling_parameters':
            if not self.samples_generated:
                # Generate samples if they don't exist
                self._generate_samples(self.settings['n_samples'])
            return self._suggest_sample(self.iter)
        
        else:
            return self._suggest_bayesian_optimization()

    def register_score(self, score, coefficients = None):
        """ Primary score registration I/O method. Registers a given score with a coefficient set.
        
        Score is mandatory. If json_mode = True, do not supply the coefficients argument. 
        If coefficients is None, then the coefficients will be read from suggestion.json (only valid for json_mode = True).
        If json_mode = False, then the coefficients must be supplied.
        This method determines whether to call _register_score_json or register_score, depending on whether json_mode is used.
        """
        if coefficients is None:
            if not self.settings['json_mode']:
                raise ValueError('You must provide a corresponding suggestion to be registered, unless turbo-RANS is in json_mode')
            else:
                # Suggestion is loaded from current json file.
                suggestion = load_json(self.directory, "suggestion.json")
                self._register_score_json(score, suggestion)
        else:
            if self.settings['json_mode']:
                self._register_score_json(score, coefficients)
            else:
                self._register_score(score, coefficients)
                self._update_database(score,coefficients)

    def _register_score_json(self, score, suggestion):
        self._get_bayesian_optimizer()
        """ Registers the score in the bayesian_optimizer object after subscribing the object to a log called history.json."""
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
        """ Registers the score in the bayesian_optimizer object."""
        self.bayesian_optimizer.register(params=suggestion, target=score)

    def _update_database(self, score, coefficients):
        """ Updates a database tracking more detailed information about the optimization. Currently only valid for json_mode = False."""
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

    def _get_bayesian_optimizer(self):
        self.bayesian_optimizer = get_optimizer(coeff_bounds=self.coeffs['bounds'],
                                                            relative_lengthscale=self.settings['kernel_relative_lengthscale'],
                                                            relative_lengthscale_bounds=self.settings['kernel_relative_lengthscale_bounds'],
                                                            nu=self.settings['kernel_nu'],
                                                            random_state=self.settings['random_state']
                                                            )
        self._condition_bayesian_optimizer()
        
        











