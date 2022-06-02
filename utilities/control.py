import os
from utilities.json_io import write_coeff_bounds

def initialize(directory = os.getcwd(),
               coeff_bounds = None,
               restart = False):
    """
    An OPTIONAL utility for restarting/writing intial coefficient bounds files. Useful for python scripting.
    """
    if coeff_bounds is None:
        print(f'Did not get coefficient bounds dict for initialization, assuming coeff_bounds.json exists in {directory}')
    else:
        write_coeff_bounds(directory, coeff_bounds)
    
    if restart: 
        try:
            print('Removing old history and suggestion files....')
            os.remove(os.path.join(directory,'history.json'))
            os.remove(os.path.join(directory,'suggestion.json'))
        except:
            print('Could not remove a file, it might not exist to start....')

    return