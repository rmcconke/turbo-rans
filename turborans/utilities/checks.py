import os

def validate_settings(optimizer):
    if optimizer.coeffs is not None:
        if 'default' in optimizer.coeffs:
            if (optimizer.coeffs['bounds'].keys() != optimizer.coeffs['default'].keys()):
                raise ValueError("You must provide default values for all coefficients")
        if optimizer.settings['n_samples'] < 5:
            raise ValueError("turbo-RANS needs at least 5 initial samples")
    
    if optimizer.settings['json_mode']:
        if optimizer.coeffs is not None and os.path.exists(os.path.join(optimizer.directory,"coeffients.json")):
            raise ValueError("Two coefficient sources given: python constructor, and coefficient file. Please provide only one.")
    
