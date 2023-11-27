from blackbox_simulation import blackbox_simulation
from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize

# Uncomment to see python logging info
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

iterations=30

# coeffs is a dict containing 'default' values (optional), and 'bounds' (required)
# You can supply the coeffs to the optimizer constructor. They will be automatically be written to coefficients.json.
# You can also just include a coefficients.json file instead, and they will be read from that.

turborans = optimizer(coeffs= {'default': {
                                            'x': .5,
                                           },
                               'bounds': {
                                            'x': [-1, 1],
                                            }},
                        #Optionally fix random seed : settings= {'random_state': 7}
                    )

for i in range(iterations):
    print(f'===== Iteration: {i} =====')
    suggestion = turborans.suggest()
    score = blackbox_simulation(suggestion)
    turborans.register_score(score=score, coefficients=suggestion)

summarize(turborans)








