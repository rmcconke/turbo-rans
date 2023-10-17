import matplotlib.pyplot as plt
import pandas as pd
import os
from turborans.utilities.json_io import load_history_loss_log
import logging
import numpy as np

def get_best_score_trend(df):
    best_target = df['target'][0]
    best_targets = []
    for i, target in enumerate(df['target']):
        if target > best_target:
            best_target = target
        best_targets.append(best_target)
    df['best_target'] = best_targets
    return df

def plot_history(directory,df_history):
    fig,ax = plt.subplots(1,2,figsize=(10,5))
    ax[0].plot(df_history.index,df_history['target'])
    ax[0].set_xlabel('Iteration')
    ax[0].set_ylabel('Objective function')
    ax[1].plot(df_history.index,df_history['best_target'])
    ax[1].set_xlabel('Iteration')
    ax[1].set_ylabel('Best objective function')
    fig.tight_layout()
    fig.savefig(os.path.join(directory,'turborans_target_history.png'),dpi=300)

def summarize(turborans_optimizer, detailed_results = True):
    if turborans_optimizer.settings['json_mode']:
        history_file = os.path.join(turborans_optimizer.directory,'history.json')
        if not os.path.exists(history_file):
            raise LookupError(f'Could not find {history_file}.')
        df_history = pd.DataFrame(load_history_loss_log(turborans_optimizer.directory,'history.json'))
    else:
        df_history = pd.DataFrame(turborans_optimizer.database)
    
    df_history.index.name='iteration'
    df_history = get_best_score_trend(df_history)
    plot_history(turborans_optimizer.directory, df_history)

    df_history.sort_values(by='target',ascending=False,inplace=True)
    print(f'=============== turbo-RANS search summary ===============')
    print(f'Iterations:   {len(df_history)}')
    print(f'Best target:  {df_history["target"].head(1).to_numpy()[0]:.4e}')
    
    print(f'Best parameters: \n*******************')
    for param in turborans_optimizer.coeffs["bounds"].keys():
        print(f'{param}: {df_history[param].head(1).to_numpy()[0]:.4e}')
    print('*******************')

    print('Search table sorted by target:')
    print(df_history)
    if detailed_results:
        logging.info('Saving summary results to turborans_history_sorted.csv')
        df_history.to_csv(os.path.join(turborans_optimizer.directory,'turborans_history_sorted.csv'))
    print(f'=========================================================')


