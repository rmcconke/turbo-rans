import logging
import os

def reset(directory, reset_settings = False):
    """ Reset a given turborans_directory by removing all previous history.json, suggestion.json, and mode.json. Optionally removes settings.json (which resets to default settings)."""
    logging.info('Removing old history and suggestion files....')
    try:
        os.remove(os.path.join(directory,'history.json'))
    except: 
        logging.info('Could not remove history.json, it might not exist to start....')
    try:
        os.remove(os.path.join(directory,'suggestion.json'))
    except: 
        logging.info('Could not remove suggestion.json, it might not exist to start....')
    try:
        os.remove(os.path.join(directory,'mode.json'))
    except:
        logging.info('Could not remove mode.json, it might not exist to start....')
    if reset_settings:
        try:
            os.remove(os.path.join(directory,'settings.json'))
        except:
            logging.info('Could not remove mode.json, it might not exist to start....')