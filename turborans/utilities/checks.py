import os

def validate_settings(optimizer):
    """ Checks if settings are valid. """

    # Check that if defaults have been given, they are given for all coefficients 
    # A current limitation. In other words, you can't supply default coeffs for one coeff, and not supply them for another coeff.
    if optimizer.coeffs is not None:
        if 'default' in optimizer.coeffs:
            if (optimizer.coeffs['bounds'].keys() != optimizer.coeffs['default'].keys()):
                raise ValueError("You must provide default values for all coefficients")
        if optimizer.settings['n_samples'] < 5: #CHANGE ME BACK AFTER HYPERPARAMETER TUNING
            raise ValueError("turbo-RANS needs at least 5 initial samples")
    
    # Check that only a single coefficients source has been provided. In json_mode, you can't have a coefficients.json file, and also call the 
    # optimizer init function with a coeffs argument - it is unclear which set of coeffs should be used.
    if optimizer.settings['json_mode']:
        if optimizer.coeffs is not None and os.path.exists(os.path.join(optimizer.directory,"coeffients.json")):
            raise ValueError("Two coefficient sources given: python constructor, and coefficient file. Please provide only one.")
    
