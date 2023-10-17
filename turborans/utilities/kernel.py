from bayes_opt import BayesianOptimization
from sklearn.gaussian_process.kernels import Matern

def derive_length_scales(bounds: dict, length_scale_delta: float = 0.1, length_scale_bounds_delta: list = [1E-2,1E1]):
    """
    :param bounds: your instance of pbounds
    :param length_scale_delta: controls the length scale; default as length scale set to 10% of bounds for each parameter
    :return: bayes_length_scales
    """
    ParameterNames = sorted(bounds.keys())
    bayes_length_scales = []
    for parameter_name in ParameterNames:
        length_scale_temp = (bounds[parameter_name][1] - bounds[parameter_name][0]) * length_scale_delta
        bayes_length_scales.append(length_scale_temp)
    bayes_length_scale_bounds = []
    for parameter_name in ParameterNames:
        length_scale_lower = (bounds[parameter_name][1] - bounds[parameter_name][0]) * length_scale_bounds_delta[0]
        length_scale_upper = (bounds[parameter_name][1] - bounds[parameter_name][0]) * length_scale_bounds_delta[1]
        bayes_length_scale_bounds.append([length_scale_lower,length_scale_upper])
    return bayes_length_scales, bayes_length_scale_bounds
    
def get_optimizer(coeff_bounds, relative_lengthscale, relative_lengthscale_bounds, nu, random_state=None):
    if random_state is not None:
        optimizer = BayesianOptimization(
            f=None,
            pbounds=coeff_bounds,
            verbose=2,
            random_state=random_state,
            allow_duplicate_points=True
        )
    else:
        optimizer = BayesianOptimization(
            f=None,
            pbounds=coeff_bounds,
            verbose=2,
            allow_duplicate_points=True
        )
    ls, ls_bounds = derive_length_scales(coeff_bounds, length_scale_delta=relative_lengthscale,
                                         length_scale_bounds_delta=relative_lengthscale_bounds)
    
    optimizer.set_gp_params(kernel=Matern(length_scale = ls,
                                          length_scale_bounds=ls_bounds,
                                          nu=nu),
                            random_state=random_state)
    return optimizer        