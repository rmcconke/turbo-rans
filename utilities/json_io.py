import os
import json
from bayes_opt.logger import JSONLogger

class newJSONLogger(JSONLogger) :

    def __init__(self, path):
            self._path=None
            super(JSONLogger, self).__init__()
            self._path = path if path[-5:] == ".json" else path + ".json"

def write_coeff_bounds(directory, coeff_bounds):
    filename = f'{os.path.join(directory,"coeff_bounds.json")}'
    with open(filename, "w") as outfile:
        json.dump(coeff_bounds, outfile, indent = 4)
    print(f'Saving coeff_bounds to {filename}')
    return filename
            
def load_coeff_bounds(directory):
    filename = f'{os.path.join(directory,"coeff_bounds.json")}'
    with open(filename, "r+") as j:
        coeff_bounds = json.load(j)
    return coeff_bounds

def load_suggestion(directory):
    filename = f'{os.path.join(directory,"suggestion.json")}'
    with open(filename, "r+") as j:
        suggestion = json.load(j)
    return suggestion

def write_suggestion(directory, suggestion):
    filename = f'{os.path.join(directory,"suggestion.json")}'
    with open(filename, "w") as outfile:
        json.dump(suggestion, outfile, indent = 4)
    print(f'Saving suggestion to {filename}')
    return filename

def load_history_to_dict(directory, file):
    data = []
    filename = f'{os.path.join(directory,file)}'
    with open(filename, "r+") as j:
        for line in j:
            data.append(json.loads(line))
    return data

