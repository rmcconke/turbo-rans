import os
import json
from bayes_opt.logger import JSONLogger
from collections import defaultdict
import logging

class newJSONLogger(JSONLogger) :
    def __init__(self, path):
            self._path=None
            super(JSONLogger, self).__init__()
            self._path = path if path[-5:] == ".json" else path + ".json"

def load_json(directory, filename):
    filename = f'{os.path.join(directory,filename)}'
    with open(filename, "r+") as j:
        data = json.load(j)
    return data
        
def write_json(directory, data, filename, append=False):
    filename = f'{os.path.join(directory,filename)}'
    if append:
        with open(filename, "a") as outfile:
            if append:
                outfile.write(json.dumps(data) + '\n')
    else:
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent = 4)
    return filename

# Rest of functions should try to call the above two
def write_coeff_bounds(directory, coeff_bounds):
    filename = write_json(directory=directory,
                          data=coeff_bounds,
                          filename="coeff_bounds.json")
    logging.info(f'Saving coeff_bounds to {filename}')
    return filename

def write_suggestion(directory, suggestion):
    filename = write_json(directory=directory,
                          data=suggestion,
                          filename="suggestion.json")
    logging.info(f'Saving suggestion to {filename}')
    return filename

def write_coeff_default(directory, coeff_default):
    filename = write_json(directory=directory,
                          data=coeff_default,
                          filename="coeff_default.json")
    logging.info(f'Saving coeff_default to {filename}')
    return filename

def load_coeff_bounds(directory=os.getcwd()):
    coeff_bounds = load_json(directory, filename="coeff_bounds.json")
    return coeff_bounds

def load_coeff_default(directory=os.getcwd()):
    coeff_default = load_json(directory, filename="coeff_default.json")
    return coeff_default

def load_suggestion(directory=os.getcwd()):
    suggestion = load_json(directory, filename="suggestion.json")
    return suggestion

def load_history_line_by_line(directory, file):
    data = []
    filename = f'{os.path.join(directory,file)}'
    with open(filename, "r+") as j:
        for line in j:
            data.append(json.loads(line))
    return data

def load_history_loss_log(directory, file):
    losses_dict = defaultdict(list)
    history = load_history_line_by_line(directory,file)
    keys = history[0].keys()
    for key in keys:
        if key == 'params':
            for param in history[0][key].keys():
                loss_list = [d[key][param] for d in history]  
                losses_dict[param]= loss_list
        elif key == 'datetime':
            pass
        else: 
            loss_list = [d[key] for d in history]  
            losses_dict[key]= loss_list
    return losses_dict
