import turborans
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from error_calcs import objective , save_plot
import file_locations as fl
from turborans.bayes_io import optimizer
from turborans.utilities.analysis import summarize
from turborans.utilities.json_io import load_json

def setCoeff(coeff):
    with open(fl.journal_file,'r') as txt:
        text=txt.readlines()
        text[25] = f'setup1.SendCommand(Command="(cx-gui-do cx-set-toggle-button2 \\"Viscous Model*Table1*ToggleBox7(k-omega Model)*GEKO\\" #t)(cx-gui-do cx-activate-item \\"Viscous Model*Table1*ToggleBox7(k-omega Model)*GEKO\\")(cx-gui-do cx-set-real-entry-list \\"Viscous Model*Table1*ToggleBox12(GEKO Options)*RealEntry3\\" \'( {coeff["csep"]}))")\n'
        text[27] = f'setup1.SendCommand(Command="(cx-gui-do cx-set-real-entry-list \\"Viscous Model*Table1*ToggleBox12(GEKO Options)*RealEntry6\\" \'( {coeff["cnw"]}))")\n'
         
        with open(fl.journal_file,'w') as txt:
            txt.writelines(text)
    

def Run():
    subprocess.run([f"C:/Program Files/ANSYS Inc/v232/Framework/bin/Win64/RunWB2.exe", "-B", "-R" f"{fl.journal_file}"])

def run_coeff(coeff:dict):
    setCoeff(coeff)
    Run()
  
for run_ind in range(30):
    optimizer(turborans_directory = fl.tuner, settings = {'json_mode': True, 'random_state':7}).suggest() 
    coeff = load_json(fl.tuner, 'suggestion.json')
    mode = load_json(fl.tuner, 'mode.json')
    run_coeff(coeff)
    score = objective(coeff)
    print(mode)
    print(coeff)
    optimizer(turborans_directory = fl.tuner, settings = {'json_mode': True, 'random_state':7}).register_score(score = score, coefficients = None)
    save_plot(run_ind)   

summarize(optimizer(turborans_directory = fl.tuner, settings = {'json_mode': True, 'random_state':7}))





