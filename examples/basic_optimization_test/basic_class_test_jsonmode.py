from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.control import reset
iterations = 20


reset('/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test', reset_settings=True)
for i in range(iterations):
    print(i)
    optimizer(turborans_directory='/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test',
                        settings= {'json_mode': True,
                    }).suggest()
    
    optimizer(turborans_directory='/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test',
                        settings= {'json_mode': True,
                    }).register_score(0.5)

summarize(optimizer(turborans_directory='/home/ryley/WDK/ML/code/turbo-rans/examples/basic_optimization_test',
                        settings= {'json_mode': True,
                    }))





