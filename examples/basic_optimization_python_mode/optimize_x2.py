from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.control import reset
import os 

directory = os.getcwd()

reset(directory, reset_settings=True)

turborans = optimizer(coeffs= {'default': {'x': -0.5,'y':2},
                               'bounds': {'x': [-1,1],'y': [-10,10]}},
                        turborans_directory=directory,
                        settings= {'json_mode': False,
                                   'force_restart': True,
                                   'random_state': 7})

for i in range(20):
    suggestion = turborans.suggest()
    print(turborans.mode)
    print(suggestion)
    turborans.register_score(score=(-suggestion['x']**2 - 0.01*suggestion['y']**2), coefficients=suggestion)

summarize(turborans)







