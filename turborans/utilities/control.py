import os
from turborans.utilities.json_io import write_coeff_bounds, write_coeff_default
import logging

def initialize(directory = os.getcwd(),
               coeff_bounds = None,
               coeff_default = None,
               restart = False):
    """
    An optional utility for restarting/writing intial coefficient bounds files. Useful for python scripting.
    """
    if coeff_bounds is None:
        logging.info(f'Did not get coefficient bounds dict for initialization, assuming coeff_bounds.json exists in {directory}')
    else:
        write_coeff_bounds(directory, coeff_bounds)
        
    if coeff_default is None:
        logging.info(f'Did not get coefficient default dict for initialization, assuming coeff_default.json exists in {directory} or is not needed')
    else:
        write_coeff_default(directory, coeff_default)
        
    if restart: 
        try:
            logging.info('Removing old history and suggestion files....')
            os.remove(os.path.join(directory,'history.json'))
            os.remove(os.path.join(directory,'suggestion.json'))
        except:
            logging.info('Could not remove a file, it might not exist to start....')
    return