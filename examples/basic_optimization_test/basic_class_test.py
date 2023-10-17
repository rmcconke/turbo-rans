from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.control import reset
iterations = 20

reset('/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test', reset_settings=True)

turborans = optimizer(coeffs= {'default': {'x': -0.5,'y':2},
                               'bounds': {'x': [-1,1],'y': [-10,10]}},
                    turborans_directory='/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test',
                    settings= {'force_restart': True,
                               'start_with_defaults_if_given':True,
                               'n_samples':5})

for i in range(iterations):
    print(turborans.mode)
    suggestion = turborans.suggest()
    print(suggestion)
    turborans.register_score(score=-suggestion['x']**2, coefficients=suggestion)

summarize(turborans)







