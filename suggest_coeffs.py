import argparse
import os
import turborans

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir","--directory", help="directory for storing files", default = os.getcwd())
    parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")

    parser.add_argument('--force_restart', help="Restart the optimization before making a suggestion.", default=False, action='store_true')
    parser.add_argument('--start_with_defaults_if_given', help="For the first suggestion, return default coefficients if they are provided.", default=True, action='store_false')
    parser.add_argument("-n_samples","--n_samples", help="Number of points to sample before calling the Bayesian optimizer.", type=int, default = 10)
    parser.add_argument("-rs","--random_state", help="random state for optimizer.", default = None, type=int)
    parser.add_argument("-u","--utility_kind", help="utility function kind: ucb, ei, or poi.", default = 'ucb')
    parser.add_argument("-k","--kappa", help="kappa parameter for utility function UCB. Higher values (e.g. 10) prefer exploration, lower values (e.g. 1) prefer exploitation. ", type=float, default = 2.0)
    parser.add_argument("-xi","--xi", help="xi parameter for utility functions EI and POI. Higher values (e.g. 0.1) prefer exploration, lower values (e.g. 1E-4) prefer exploitation.", type=float, default = 0.1)
    parser.add_argument("-rls","--kernel_relative_lengthscale", help="Initial length scale for the Gaussian process will be determined by rls*(upper_bounds-lower-bound)", type=float, default = 0.1)
    parser.add_argument("-rls_l_b","--kernel_relative_ls_lowerbound", help="Relative lower bound for the GP lengthscale optimization", type=float, default = 1E-2)
    parser.add_argument("-rls_u_b","--kernel_relative_ls_upperbound", help="Relative upper bound for the GP lengthscale optimization", type=float, default = 1E1)
    parser.add_argument("-nu","--kernel_nu", help="nu value for the Matern kernel", type=float, default = 5/2)

    args = parser.parse_args()
    turborans.optimizer(turborans_directory=args.directory,
                        settings = {
                                    'force_restart': args.force_restart,
                                    'start_with_defaults_if_given': args.start_with_defaults_if_given,
                                    'json_mode': True,
                                    'n_samples': args.n_samples,
                                    'random_state': args.random_state,
                                    'bo_utility_kind': args.utility_kind,
                                    'bo_kappa': args.kappa,
                                    'bo_xi': args.xi,
                                    'kernel_relative_lengthscale': args.kernel_relative_lengthscale,
                                    'kernel_relative_lengthscale_bounds': [args.kernel_relative_ls_lowerbound,args.kernel_relative_ls_upperbound],
                                    'kernel_nu': args.kernel_nu
                                    }
                        ).suggest()
    