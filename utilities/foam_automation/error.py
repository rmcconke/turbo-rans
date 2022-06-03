import os
import openfoamparser as Ofpp
from scipy.interpolate import griddata
#from dataFoam.utilities.foamIO.readFoam import get_cell_centres
from sklearn.metrics import mean_squared_error
import numpy as np

def get_cell_centres(foamdirectory):
    if not os.path.exists(os.path.join(foamdirectory,'0','C')):
        os.system(f"postProcess -func writeCellCentres -time 0 -case {foamdirectory} > {os.path.join(foamdirectory,'log.writeCellCentres')}")
    mesh = Ofpp.FoamMesh(foamdirectory)
    mesh.read_cell_centres(os.path.join(foamdirectory,'0/C'))
    return mesh.cell_centres

def map_to_reference(fields,points,points_ref,method='linear'):
    fields_mapped = griddata(points,fields,points_ref,method=method)
    return fields_mapped
                     

def mseU_2Dxy(foamdirectory = os.getcwd(),
             foamtime = None,
             ref_df = None,
             interp_method='linear'):
    foamdirectory = os.path.abspath(foamdirectory)
    U_sim = Ofpp.parse_internal_field(os.path.join(foamdirectory,foamtime,'U'))[:,0:2]
    points_sim = get_cell_centres(foamdirectory)[:,0:2]
    U_sim_mapped = map_to_reference(U_sim,points_sim,ref_df[['x','y']].values,method=interp_method)                           
    U_ref = ref_df[['Ux','Uy']].values
    mse = mean_squared_error(U_ref,U_sim_mapped)
    return mse

def mseU_2Dmag(foamdirectory = os.getcwd(),
             foamtime = None,
             ref_df = None,
             interp_method='linear'):
    foamdirectory = os.path.abspath(foamdirectory)
    U_sim = Ofpp.parse_internal_field(os.path.join(foamdirectory,foamtime,'U'))[:,0:2]
    points_sim = get_cell_centres(foamdirectory)[:,0:2]
    U_sim_mapped = map_to_reference(U_sim,points_sim,ref_df[['x','y']].values,method=interp_method)             
    U_ref = ref_df[['Ux','Uy']].values
    U_sim_mapped_mag = np.linalg.norm(U_sim_mapped,axis=1)
    U_ref_mag = np.linalg.norm(U_ref,axis=1)
    print(U_ref_mag.shape)
    print(U_ref_mag[0])
    print(U_ref[0,:])
    mse = mean_squared_error(U_ref_mag,U_sim_mapped_mag)
    return mse

def mseU_2Dmag_relcoeff(foamdirectory = os.getcwd(),
                        foamtime = None,
                        ref_df = None,
                        interp_method='linear',
                        coef = None,
                        coef_default = None
                       ):
    foamdirectory = os.path.abspath(foamdirectory)
    U_sim = Ofpp.parse_internal_field(os.path.join(foamdirectory,foamtime,'U'))[:,0:2]
    points_sim = get_cell_centres(foamdirectory)[:,0:2]
    U_sim_mapped = map_to_reference(U_sim,points_sim,ref_df[['x','y']].values,method=interp_method)             
    U_ref = ref_df[['Ux','Uy']].values
    U_sim_mapped_mag = np.linalg.norm(U_sim_mapped,axis=1)
    U_ref_mag = np.linalg.norm(U_ref,axis=1)
    print(U_ref_mag.shape)
    print(U_ref_mag[0])
    print(U_ref[0,:])
    mse = mean_squared_error(U_ref_mag,U_sim_mapped_mag)
    rel_coef = (coef-coef_default)/coef_default
    score = mse + rel_coef
    return score

def foam_mse(ref_df):
    U_sim = Ofpp.parse_internal_field('foam/case_1p0/5000/U')[:,0:2]
    mse = mean_squared_error(ref_df[['Ux','Uy']].values,U_sim)
    print('MSE: '+ str(mse))
    return mse