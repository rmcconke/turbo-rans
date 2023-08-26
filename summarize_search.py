import argparse
import os
import turborans

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir","--directory", help="directory for storing files", default = os.getcwd())
    parser.add_argument("score", help="score to add to the history", type=float)
    parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")
    args = parser.parse_args()
    turborans.register_score(score = args.score,
                   directory = args.directory)
