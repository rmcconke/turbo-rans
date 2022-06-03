import os
import json
from bayes_opt.logger import JSONLogger

class newJSONLogger(JSONLogger) :

    def __init__(self, path):
            self._path=None
            super(JSONLogger, self).__init__()
            self._path = path if path[-5:] == ".json" else path + ".json"

def write_json(directory, data, filename):
    filename = f'{os.path.join(directory,filename)}'
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent = 4)
    return filename
            
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
    filename = f'{os.path.join(directory,"coeff_bounds.json")}'
    with open(filename, "r+") as j:
        coeff_bounds = json.load(j)
    return coeff_bounds

def load_coeff_default(directory):
    filename = f'{os.path.join(directory,"coeff_default.json")}'
    with open(filename, "r+") as j:
        coeff_default = json.load(j)
    return coeff_default

def load_suggestion(directory):
    filename = f'{os.path.join(directory,"suggestion.json")}'
    with open(filename, "r+") as j:
        suggestion = json.load(j)
    return suggestion

def load_history_to_dict(directory, file):
    data = []
    filename = f'{os.path.join(directory,file)}'
    with open(filename, "r+") as j:
        for line in j:
            data.append(json.loads(line))
    return data

