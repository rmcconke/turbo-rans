import os
import json
from bayes_opt.logger import JSONLogger
from collections import defaultdict

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
    #if append:
    #    with open(filename) as f:
    #       data = json.load(f)
    #    data.update(a_dict)
    if append:
        with open(filename, "a") as outfile:
            if append:
                outfile.write(json.dumps(data) + '\n')
    else:
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent = 4)
        #consider f.write(json.dumps(data) + "\n") (dumps as well)
    return filename

# Rest of function should try to call the above two
def write_coeff_bounds(directory, coeff_bounds):
    filename = write_json(directory=directory,
                          data=coeff_bounds,
                          filename="coeff_bounds.json")
    print(f'Saving coeff_bounds to {filename}')
    return filename

def write_suggestion(directory, suggestion):
    filename = write_json(directory=directory,
                          data=suggestion,
                          filename="suggestion.json")
    print(f'Saving suggestion to {filename}')
    return filename

def write_coeff_default(directory, coeff_default):
    filename = write_json(directory=directory,
                          data=coeff_default,
                          filename="coeff_default.json")
    print(f'Saving coeff_default to {filename}')
    return filename

def load_coeff_bounds(directory):
    coeff_bounds = load_json(directory, filename="coeff_bounds.json")
    return coeff_bounds

def load_coeff_default(directory):
    coeff_default = load_json(directory, filename="coeff_default.json")
    return coeff_default

def load_suggestion(directory):
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

# Delete these soon
def sload_history_to_params_target(directory, file):
    history = load_history_to_dict(directory,file)
    param = [d['params']['a1'] for d in history]
    target = [d['target'] for d in history]  
    return param, target

def sload_loss_log_to_params_target(directory, file, target):
    history = load_history_to_dict(directory,file)
    param = [d['params']['a1'] for d in history]
    target = [d[target] for d in history]  
    return param, target
