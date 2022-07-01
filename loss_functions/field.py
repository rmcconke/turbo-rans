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
    print(f'mapeU {mapeU}')
    print(f'mapek {mapek}')
    print(f'error_term {mapeU+mapek}')
    print(f'relcoeff {relcoeff}')
    print(f'score {score}')
    return score

def multi_mape_U_magnitude_2Dxy_mape_k(U_ref, U_sim_mapped, k_ref, k_sim_mapped):
    mapeU = mape_U_magnitude_2Dxy(U_ref, U_sim_mapped)
    mapek = mape_k(k_ref, k_sim_mapped)
    score = (mapeU + mapek)
    return score
