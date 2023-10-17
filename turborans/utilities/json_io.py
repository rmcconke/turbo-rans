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
            date_list = [d[key]['datetime'] for d in history]  
            losses_dict[key]= date_list
        else: 
            loss_list = [d[key] for d in history]  
            losses_dict[key]= loss_list
    return losses_dict
