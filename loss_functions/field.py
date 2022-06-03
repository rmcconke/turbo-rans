from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import os

def mse_U_componentwise_2Dxy(U_ref, U_sim_mapped):
    mse = mean_squared_error(U_ref,U_sim_mapped)
    return mse

def mse_U_magnitude_2Dxy(U_ref, U_sim_mapped):
    U_sim_mapped_mag = np.linalg.norm(U_sim_mapped,axis=1)
    U_ref_mag = np.linalg.norm(U_ref,axis=1)
    mse = mean_squared_error(U_ref_mag,U_sim_mapped_mag)
    return mse

def mape_U_magnitude_2Dxy(U_ref, U_sim_mapped):
    U_sim_mapped_mag = np.linalg.norm(U_sim_mapped,axis=1)
    U_ref_mag = np.linalg.norm(U_ref,axis=1)
    mape = mean_absolute_percentage_error(U_ref_mag,U_sim_mapped_mag)
    return mape

def mape_k(k_ref, k_sim_mapped):
    mape = mean_absolute_percentage_error(k_ref,k_sim_mapped)
    return mape

def mean_relcoeff(coeff_dict, coeff_default):
    coeffs = np.asarray(list(coeff_dict.values()))
    defaults = np.asarray(list(coeff_default.values()))
    mean_relcoeff = np.mean(
        np.abs(
        np.divide( (coeffs - defaults),
                  defaults)
        ))
    return mean_relcoeff

def multi_mse_U_magnitude_2Dxy_relcoeff_mean(U_ref, U_sim_mapped, coeff_dict, coeff_default, lda=1.0):
    mse = mse_U_magnitude_2Dxy(U_ref, U_sim_mapped)
    relcoeff = mean_relcoeff(coeff_dict, coeff_default)
    score = mse*(1+lda*relcoeff)
    return score

def multi_mape_U_magnitude_2Dxy_relcoeff_mean(U_ref, U_sim_mapped, coeff_dict, coeff_default, lda=1.0):
    mape = mape_U_magnitude_2Dxy(U_ref, U_sim_mapped)
    relcoeff = mean_relcoeff(coeff_dict, coeff_default)
    score = mape*(1+lda*relcoeff)
    return score

def multi_mape_U_magnitude_2Dxy_mape_k_relcoeff_mean(U_ref, U_sim_mapped, k_ref, k_sim_mapped, coeff_dict, coeff_default, lda=1.0):
    mapeU = mape_U_magnitude_2Dxy(U_ref, U_sim_mapped)
    mapek = mape_k(k_ref, k_sim_mapped)
    relcoeff = mean_relcoeff(coeff_dict, coeff_default)
    score = (mapeU + mapek)*(1+lda*relcoeff)
    return score

def multi_mape_U_magnitude_2Dxy_mape_k(U_ref, U_sim_mapped, k_ref, k_sim_mapped):
    mapeU = mape_U_magnitude_2Dxy(U_ref, U_sim_mapped)
    mapek = mape_k(k_ref, k_sim_mapped)
    score = (mapeU + mapek)
    return score

#below bad
def mse_U_magnitude_2Dxy_bad(foamdirectory = os.getcwd(),
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
    return mse

def mseU_2Dmag_relcoeff(foamdirectory = os.getcwd(),
                        foamtime = None,
                        ref_df = None,
                        interp_method='linear',
                        coeff = None,
                        coeff_default = None
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
    rel_coeff = abs(coeff-coeff_default)/coeff_default
    score = mse + mse*rel_coeff
    return score

def mseU_2Dmagrel_krel_relcoeff(foamdirectory = os.getcwd(),
                        foamtime = None,
                        ref_df = None,
                        interp_method='linear',
                        coeff = None,
                        coeff_default = None
                       ):
    foamdirectory = os.path.abspath(foamdirectory)
    U_sim = Ofpp.parse_internal_field(os.path.join(foamdirectory,foamtime,'U'))[:,0:2]
    k_sim = Ofpp.parse_internal_field(os.path.join(foamdirectory,foamtime,'k'))

    points_sim = get_cell_centres(foamdirectory)[:,0:2]
    U_sim_mapped = map_to_reference(U_sim,points_sim,ref_df[['x','y']].values,method=interp_method)   
    k_sim_mapped = map_to_reference(k_sim,points_sim,ref_df[['x','y']].values,method=interp_method)             

    U_ref = ref_df[['Ux','Uy']].values
    k_ref = ref_df['k'].values

    U_sim_mapped_mag = np.linalg.norm(U_sim_mapped,axis=1)
    U_ref_mag = np.linalg.norm(U_ref,axis=1)
    
    #mse = mean_squared_error(U_ref_mag,U_sim_mapped_mag)
    rel_U = mean_absolute_percentage_error(U_ref_mag,U_sim_mapped_mag)
    rel_k = mean_absolute_percentage_error(k_ref,k_sim_mapped)
    rel_coeff = abs(coeff-coeff_default)/coeff_default
    score = (rel_U+rel_k)*(1+0.5*rel_coeff)
    return score