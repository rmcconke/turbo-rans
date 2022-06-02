import os
import json
from bayes_opt.logger import JSONLogger

class newJSONLogger(JSONLogger) :

      def __init__(self, path):
            self._path=None
            super(JSONLogger, self).__init__()
            self._path = path if path[-5:] == ".json" else path + ".json"

def load_coeff_bounds(directory):
    filename = f'{os.path.join(directory,"coeff_bounds.json")}'
    with open(filename, "r+") as j:
        coeff_bounds = json.load(j)
    return coeff_bounds, filename

def load_suggestion(directory):
    filename = f'{os.path.join(directory,"suggestion.json")}'
    with open(filename, "r+") as j:
        suggestion = json.load(j)
    return suggestion, filename

def write_suggestion(directory, suggestion):
    filename = f'{os.path.join(directory,"suggestion.json")}'
    with open(filename, "w") as outfile:
        json.dump(suggestion, outfile, indent = 4)
    print(f'Saving suggestion to {filename}')
    return filename