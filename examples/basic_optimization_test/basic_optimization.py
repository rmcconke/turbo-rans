import numpy as np
import os
import pandas as pd
from turborans.utilities.foam_automation.caserunner import run_until_convergence, get_endtime
from turborans.utilities.foam_automation.foamLossFunc import foamFieldLossFunc
from turborans.utilities.foam_automation.set_foam_coeff import set_foam_coef
from turborans.utilities.json_io import write_suggestion, write_json, load_coeff_default, load_coeff_bounds, load_history_loss_log, load_suggestion
from turborans.utilities.control import initialize
from turborans.bayes_io import suggest, register_score, summarize
import logging
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import random
from bayes_opt import UtilityFunction, BayesianOptimization
from sklearn.gaussian_process.kernels import Matern
import matplotlib.pyplot as plt
from matplotlib import gridspec

tunerdir = os.path.join(os.getcwd(),'examples','basic_optimization_test') # Directory for turbo-rans files
iterations=20 # For loop could also be changed to run until some sort of convergence or loss function tolerance
n_points_sampled = 4 # We sample 4 random points before beginning Bayesian optimization, this is optional
utility = 'ucb' # Optimizer parameter
xi = 0.1 # Optimizer parameter
kappa = 2


initialize(directory = tunerdir,
           coeff_bounds = {'x': [-1,1]},
           coeff_default = {'x': -0.5},
           restart = True) #Sets up turbo-rans files and clears past history if restart==True

np.random.seed(7)
score_best = 1E6 

def get_optimizer(coeff_bounds, nu=5/2):
    optimizer = BayesianOptimization(
        f=None,
        pbounds=coeff_bounds,
        verbose=2,
        allow_duplicate_points=True
    )
    optimizer.set_gp_params(kernel=Matern(length_scale = [0.1], nu=nu))
    return optimizer

optimizer = get_optimizer({'x': [-1,1]})

def target(x):
    return -x**2 + 1#np.exp(-(x - 2)**2) + np.exp(-(x - 6)**2/10) + 1/ (x**2 + 1)



x = np.linspace(-1, 1, 1000).reshape(-1, 1)
y = target(x)


def posterior(optimizer, x_obs, y_obs, grid):
    optimizer._gp.fit(x_obs, y_obs)

    mu, sigma = optimizer._gp.predict(grid, return_std=True)
    return mu, sigma

def plot_gp(optimizer, x, y):
    fig = plt.figure(figsize=(16, 10))
    steps = len(optimizer.space)
    fig.suptitle(
        'Gaussian Process and Utility Function After {} Steps'.format(steps),
        fontdict={'size':30}
    )
    
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    axis = plt.subplot(gs[0])
    acq = plt.subplot(gs[1])
    
    x_obs = np.array([[res["params"]["x"]] for res in optimizer.res])
    y_obs = np.array([res["target"] for res in optimizer.res])
    
    mu, sigma = posterior(optimizer, x_obs, y_obs, x)
    axis.plot(x, y, linewidth=3, label='Target')
    axis.plot(x_obs.flatten(), y_obs, 'D', markersize=8, label=u'Observations', color='r')
    axis.plot(x, mu, '--', color='k', label='Prediction')

    axis.fill(np.concatenate([x, x[::-1]]), 
              np.concatenate([mu - 1.9600 * sigma, (mu + 1.9600 * sigma)[::-1]]),
        alpha=.6, fc='c', ec='None', label='95% confidence interval')
    
    axis.set_xlim((-1, 1))
    axis.set_ylim((None, None))
    axis.set_ylabel('f(x)', fontdict={'size':20})
    axis.set_xlabel('x', fontdict={'size':20})
    
    utility_function = UtilityFunction(kind="ucb", kappa=5, xi=0)
    utility = utility_function.utility(x, optimizer._gp, 0)
    acq.plot(x, utility, label='Utility Function', color='purple')
    acq.plot(x[np.argmax(utility)], np.max(utility), '*', markersize=15, 
             label=u'Next Best Guess', markerfacecolor='gold', markeredgecolor='k', markeredgewidth=1)
    acq.set_xlim((-1, 1))
    acq.set_ylim((0, np.max(utility) + 0.5))
    acq.set_ylabel('Utility', fontdict={'size':20})
    acq.set_xlabel('x', fontdict={'size':20})
    
    axis.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    acq.legend(loc=2, bbox_to_anchor=(1.01, 1), borderaxespad=0.)

n_sample = 5
x_rand = np.random.uniform(-1, 1, size=(n_sample)) #Initial random points


for i in range(iterations):    
    if i == 0: # First iteration uses default coefficients, so the suggestion is the default coefficient
        #search_point=load_coeff_default(directory=tunerdir)
        #write_suggestion(directory=tunerdir, suggestion=search_point)
        search_point = {'x':-0.5}
        #write_suggestion(directory=tunerdir, suggestion=search_point)
    elif i <=n_sample:
        search_point = {'x': x_rand[i-1]}
    #elif i < n_points_sampled: # Next iterations use random coefficients
    #    search_point = {"a1": a1_rand[i], "betaStar": betaStar_rand[i]}
    #    write_suggestion(directory=tunerdir, suggestion=search_point)
    else: # Coefficients for remaining iterations are suggested by the optimizer
        utility = UtilityFunction(kind='ucb', kappa=kappa, xi=xi)
        search_point = optimizer.suggest(utility)
        #write_suggestion(directory=tunerdir, suggestion=search_point)

        #suggest(directory=tunerdir, utility_kind = utility, kappa=2, xi=xi)
    #suggest(directory=tunerdir, random_state=7,utility_kind = utility, xi=xi)

    #search_point = load_suggestion(directory=tunerdir)
    print(f'=====================================\nIteration: {i}\n=====================================')
    print(search_point)
    score = target(search_point['x'])
    optimizer.register(params=search_point, target=score)      
    plot_gp(optimizer, x, y)             
    #register_score(score=score, directory=tunerdir) # Register the loss function with the optimizer

#summarize(directory=tunerdir)
