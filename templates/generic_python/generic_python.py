from blackbox_simulation import blackbox_simulation
from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.control import reset

# Uncomment to see python logging info
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

iterations=30

# coeffs is a dict containing 'default' values (optional), and 'bounds' (required)

turborans = optimizer(coeffs= {'default': {
                                            'a1': 0.31,
                                           },
                               'bounds': {
                                            'a1': [0.25,0.4],
                                            }},
                        settings= {'force_restart': True,
                                   'random_state': 7})

for i in range(iterations):
    print(f'===== Iteration: {i} =====')
    suggestion = turborans.suggest()
    score = blackbox_simulation(suggestion)
    turborans.register_score(score=score, coefficients=suggestion)

summarize(turborans)








