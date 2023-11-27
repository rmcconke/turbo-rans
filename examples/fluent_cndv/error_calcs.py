import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import file_locations as fl
from turborans.loss_functions.GEDCP import gedcp
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 1.0
mpl.rcParams['axes.linewidth'] = 0.5 
mpl.rcParams['xtick.major.size'] = 3.5 
mpl.rcParams['ytick.major.size'] = 3.5 
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["k"]) 
mpl.rcParams['xtick.major.width'] = 0.5 
mpl.rcParams['ytick.major.width'] = 0.5 
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams["font.family"] = "Times New Roman"
rc = {"font.family" : "serif", 
      "mathtext.fontset" : "stix",
      'font.size'   : 10}
plt.rcParams.update(rc)
mpl.rcParams['text.usetex'] == True
plt.rcParams["font.serif"] = ["Times New Roman"]
plt.rcParams["lines.solid_joinstyle"]='miter'
params = {'legend.fontsize': 10,
          'legend.frameon': True,
          'legend.borderpad': 0.3,
          'legend.handlelength': 0.75,
          'legend.handletextpad': 0.1,
          'legend.labelspacing':0,
          'legend.fancybox': False,
          'legend.edgecolor': 'k',
          'patch.linewidth':0.5,
          'savefig.format': 'pdf',
          'savefig.bbox': 'tight'}
print(plt.rcParams.keys())
plt.rcParams.update(params)


def getDNSdata(FileName):
    getdata = np.genfromtxt(FileName, dtype = None, skip_header = 26)
    x_dns = getdata[:,0]
    cp_dns= (getdata[:,4]) - getdata[-1,4]
    return x_dns, cp_dns


def getSimData(FileName):
    getdata = np.genfromtxt(FileName, dtype=None, skip_header=6, delimiter=",")
    x_sim = getdata[:, 0]
    cp_sim = (getdata[:,3] - getdata[610, 3])/0.4 #Umax value changed
    inds = x_sim.argsort()
    return x_sim[inds], cp_sim[inds]


def objective(current_coef):
    
    x_dns, cp_dns = getDNSdata(fl.dns)
    x_sim, cp_sim = getSimData(fl.sim)
    inds = [250, 350, 500, 560, 640, 770, 980, 1200, 1500, 1700]
    x_new = x_dns[inds]
    #cp resampled
    cp_sim_resampled = np.interp(x_new, x_sim, cp_sim)
    cp_dns_resampled = cp_dns[inds]
    obj_value = gedcp(field_sim_mapped_dict = {"cp": cp_sim_resampled}, field_ref_dict = {"cp": cp_dns_resampled}, coef_default_dict = {"csep": 1.75, "cnw": 0.5}, coef_dict = current_coef, lda_dict = {'coef': 0.5})
    return obj_value


def save_plot(iteration):
    x_dns, cp_dns = getDNSdata(fl.dns)
    x_sim, cp_sim = getSimData(fl.sim)
    x_base, cp_base = getSimData(fl.baseline)
    #cp resampled
    cp_sim_resampled = np.interp(x_dns, x_sim, cp_sim)
    cp_base_resampled = np.interp(x_dns, x_base, cp_base)
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(6.69,2.5))

    ax.plot(x_dns, cp_dns, 'b--', label = "DNS")
    
    ax.plot(x_dns, cp_base_resampled, 'g', label = "GEKO")

    ax.plot(x_dns, cp_sim_resampled, 'r', label = "GEKO (turbo-RANS)")

   
    ind = [250, 350, 500, 560, 640, 770, 980, 1200, 1500, 1700]
    ax.scatter(x_dns[ind], cp_dns[ind], c = "b", s = 5)
    ax.scatter(x_dns[ind], cp_base_resampled[ind], c = "g", s = 5 )
    ax.scatter(x_dns[ind], cp_sim_resampled[ind], c = "r", s = 5)
    
    ax.set_xlabel(r'$x/H$')
    ax.set_ylabel(r'$C_p$')
    ax.set_xlim([0,12])
    ax.set_ylim([-1.6, 0.4])
    ax.set_xticks([0,2,4,6,8,10,12])
    ax.set_yticks([-1.6, -1.2, -0.8, -0.4, 0, 0.4])
    ax.legend(loc = "lower right")
    fig.tight_layout()
      
    fig.savefig(f"{fl.figs}/Pressure_coeff{iteration}.pdf")

#save_plot(30)
