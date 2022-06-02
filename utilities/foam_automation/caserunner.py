from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
import os
def get_endtime(case = os.getcwd()):
    dire=SolutionDirectory(case)
    endtime = dire.getLast()
    return endtime

def run_until_convergence(case = os.getcwd(), solver = 'simpleFoam', n_proc = None):
    dire=SolutionDirectory(case)
    dire.clearResults(removeProcs=True)
    if n_proc is not None:
        decomposeUtil=UtilityRunner(argv=['decomposePar','-force','-case',case],silent=True,logname="decomposePar")#logname=os.path.join(case,"decomposePar"))
        decomposeUtil.start()
        run=ConvergenceRunner(BoundingLogAnalyzer(),argv=[f'mpirun -n {n_proc} {solver}','-parallel','-case',case],silent=True,logname="PyFoamSolve")
        run.start()
        reconstructUtil=UtilityRunner(argv=['reconstructPar','-latestTime','-case',case],silent=True,logname="reconstructPar")
        reconstructUtil.start()
        os.system(f'rm -r {os.path.join(case,"processor*")}')
    else:
        run=ConvergenceRunner(BoundingLogAnalyzer(),argv=[f'{solver}','-case',case],silent=True,logname="PyFoamSolve")
        run.start()
    
    last_time = dire.getLast()
    return last_time
