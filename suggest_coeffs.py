import argparse
import os
import turborans

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir","--directory", help="directory for storing files", default = os.getcwd())
    parser.add_argument("-k","--kappa", help="kappa parameter for utility function UCB. Higher values (e.g. 10) prefer exploration, lower values (e.g. 1) prefer exploitation. ", type=float, default = 2.0)
    parser.add_argument("-xi","--xi", help="xi parameter for utility functions EI and POI. Higher values (e.g. 0.1) prefer exploration, lower values (e.g. 1E-4) prefer exploitation.", type=float, default = 0.1)
    parser.add_argument("-u","--utility_kind", help="utility function kind, UCB/EI/POI.", default = 'poi')
    parser.add_argument("-rs","--random_state", help="random state for optimizer.", default = None)
    parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")
    args = parser.parse_args()
    turborans.suggest(directory = args.directory,
            kappa = args.kappa,
            xi = args.xi,
            utility_kind = args.utility_kind,
            random_state = args.random_state)
    