import argparse
import os
import turborans
from turborans.utilities.analysis import summarize

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory containing .json files to be summarized", default = os.getcwd())
    parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")
    args = parser.parse_args()

    summarize(turborans.bayes_io.optimizer(turborans_directory=args.directory,
                            settings= {'json_mode': True,}))

