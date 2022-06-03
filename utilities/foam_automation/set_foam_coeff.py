import fileinput
import sys
import os

def set_foam_coef(foamdir,coeffs):
    for coef in coeffs:
        entry = coef
        value = coeffs[coef]
        # Changes an entry in the turbulenceProperties dict that starts with entry to be value
        for line in fileinput.input(os.path.join(foamdir,'constant/turbulenceProperties'), inplace=True):
            if line.strip().startswith(entry):
                line = '\t'+entry+'\t'+ str(value) + ';\n'
            sys.stdout.write(line)
    return