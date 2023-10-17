from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

def gedcp(field_sim_mapped_dict = {},
          field_ref_dict = {},
          integral_param_sim_dict = {},
          integral_param_ref_dict = {},
          coef_default_dict = {},
          coef_dict = {},
          lda_dict = {'coef': 0.5},
          error_type = 'mape'):
    '''
    General error and default coefficient preference (GEDCP) loss function. Combined errors in fields and integral parameters with preference for default coefficients.
    
    Score = e * ( 1 + lda_coeff * rel_coeff)
    e = field MAPEs + integral parameter MAPEs
    rel_coeff = mean relative change in coefficent (mean over all coefficients)

            Parameters:
                    field_sim_mapped_dict: A dictionary of field names and corresponding field values (should already be mapped onto the reference locations). e.g. {'U': array_U, 'k': array_k}
                    field_ref_dict: A dictionary of field names and reference values e.g {'U': array_U_ref, 'k': array_k_ref}
                    integral_param_sim_dict: A dictionary of integral parameters and values from simulation, e.g. {'Cl': 1.5, 'Cd': 0.1}
                    integral_param_sim_dict: A dictionary of integral parameters and values from reference, e.g. {'Cl': 1.3, 'Cd': 0.12}
                    coef_default_dict: A dictionary of default coefficient values, e.g. {'a1': 0.31, 'betaStar': 0.09}
                    coef_dict: A dictionary of current coefficient values, e.g. {'a1:0.30, 'betaStar': 0.1}
                    lda_dict: A dictionary of lambda values. Lambda values can be supplied for a field, integral parameter, and the coef lambda is also contained in this dict.
                    error_type: MAPE or MSE. Note that MAPE is recommended due to scale differences between MSE of different variables.
                    
            Returns:
                    score
    '''
    error_term = 0.0
    for field in field_sim_mapped_dict.keys():
        assert field in field_ref_dict.keys(), "Sim fields should have a corresponding reference value"
        if error_type == 'mape':
            error_i = mean_absolute_percentage_error(field_ref_dict[field],field_sim_mapped_dict[field])
        elif error_type == 'mse':
            error_i = mean_squared_error(field_ref_dict[field],field_sim_mapped_dict[field])
        else: 
            raise NotImplemented(f'Error type {error_type} calculation not implemented')

        if field in lda_dict.keys():
            lda = lda_dict[field]
        else: lda = 1.0

        error_term += lda*error_i

    for integral_parameter in integral_param_ref_dict.keys():
        assert integral_parameter in integral_param_ref_dict.keys(), "Sim integral parameters should have a corresponding reference value"
        if error_type == 'mape':
            error_i = mean_absolute_percentage_error([integral_param_ref_dict[integral_parameter]],[integral_param_sim_dict[integral_parameter]])
        elif error_type == 'mse':
            error_i = mean_squared_error([integral_param_ref_dict[integral_parameter]],[integral_param_sim_dict[integral_parameter]])
        else: 
            raise NotImplemented(f'Error type {error_type} calculation not implemented')
        if integral_parameter in lda_dict.keys():
            lda = lda_dict[integral_parameter]
        else: lda = 1.0

        error_term += lda*error_i

    coefs = np.asarray(list(coef_dict.values()))
    defaults = np.asarray(list(coef_default_dict.values()))
    coef_term = np.mean(
        np.abs(
        np.divide( (coefs - defaults),
              defaults)
        ))
    score = error_term*(1 + lda_dict['coef']*coef_term)
    return score