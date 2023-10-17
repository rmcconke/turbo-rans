from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.control import reset
from turborans.utilities.json_io import load_json
import os

directory = os.getcwd()
def black_box_function():
    coeffs = load_json(directory,'suggestion.json')
    return -coeffs['x']**2 - 0.01*coeffs['y']**2

reset(directory, reset_settings=True)
for i in range(20):
    print(i)
    optimizer(turborans_directory=directory,
                        settings= {'json_mode': True,'random_state':7
                    }).suggest()
    print(load_json(directory,'mode.json')['mode'])
    print(load_json(directory,'suggestion.json'))
    optimizer(turborans_directory=directory,
                        settings= {'json_mode': True,'random_state':7
                    }).register_score(black_box_function())

summarize(optimizer(turborans_directory=directory,
                        settings= {'json_mode': True,'random_state':7
                    }))





