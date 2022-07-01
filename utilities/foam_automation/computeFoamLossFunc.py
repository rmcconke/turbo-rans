import os
import openfoamparser as Ofpp
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pandas as pd

class computeFoamFieldLossFunc():
    def __init__(self, foamdir, ref_df, interp_method='nearest', read_cell_centres = True):
        self.foamdir=os.path.abspath(foamdir)
        self.ref_df=ref_df
        self.interp_method=interp_method
        
        if read_cell_centres:
            self.get_cell_centres()

    def get_cell_centres(self):
        if not os.path.exists(os.path.join(self.foamdir,'0','C')):
            os.system(f"postProcess -func writeCellCentres -time 0 -case {self.foamdir} > {os.path.join(self.foamdir,'log.writeCellCentres')}")
        mesh = Ofpp.FoamMesh(self.foamdir)
        mesh.read_cell_centres(os.path.join(self.foamdir,'0/C'))
        self.cell_centres = mesh.cell_centres
        return 

    def map_to_reference(self,fieldname):
        field = Ofpp.parse_internal_field(os.path.join(self.foamdir,self.foamtime,fieldname))
        field_mapped = griddata(self.cell_centres,
                                 field,
                                 self.ref_df[['x','y','z']],
                                 method=self.interp_method)
        return field_mapped
    def read_force_coefficient(self,coef_name):
        #foamdir = '/home/ryley/ML/foam/run/turbo-rans/bayesian_a1_betaStar_airfoil/airfoil_template'
        #tunerdir = os.path.join(foamdir,'tuner')
        #ref_df = pd.read_csv(os.path.join(tunerdir,'refdata.csv'))

        #ref_df.describe()
        #print(ref_df['Cl'][0])

        df = pd.read_csv(os.path.join(self.foamdir,'postProcessing/forceCoeffs1/0/coefficient_0.dat'),delimiter ='\t',skiprows = 12)
        df.columns = df.columns.str.replace(' ', '')
        return float(df[coef_name].iloc[-1])
        
    def foam_general_loss_function(self, foamtime,
                                     coef_default_dict,
                                     coef_dict,
                                     error_calc_fields,
                                     error_calc_intparams,
                                     lda_dict={'coef': 0.5},
                                     error_type = 'mape'):
        self.foamtime = foamtime
        error_term = 0.0
        for field in error_calc_fields:
            if field == 'U':
                field_ref=np.linalg.norm(self.ref_df[['Ux','Uy']].values,axis=1)
                field_sim_mapped=np.linalg.norm(self.map_to_reference('U')[:,0:2],axis=1)
            elif field == 'k':
                field_ref=self.ref_df['k'].values
                field_sim_mapped=self.map_to_reference('k')
            else:
                raise NotImplemented(f'Field {field} error calculation not implemented')
                
            if error_type == 'mape':
                error_i = mean_absolute_percentage_error(field_ref,field_sim_mapped)
            elif error_type == 'mse':
                error_i = mean_squared_error(field_ref,field_sim_mapped)
            else: 
                raise NotImplemented(f'Error type {error_type} calculation not implemented')
                
            if field in lda_dict.keys():
                lda = lda_dict[field]
            else: lda = 1.0
            
            error_term += lda*error_i
            
        for integral_parameter in error_calc_intparams:
            if integral_parameter == 'Cl':
                integral_parameter_ref = float(self.ref_df[integral_parameter][0])
                integral_parameter_sim = self.read_force_coefficient('Cl')
                print(integral_parameter_ref)
                print(integral_parameter_sim)
            elif integral_parameter == 'Cd':
                integral_parameter_ref = self.ref_df[integral_parameter][0]
                integral_parameter_sim = self.read_force_coefficient('Cd')
                print(integral_parameter_ref)
                print(integral_parameter_sim)     
                
            if error_type == 'mape':
                error_i = mean_absolute_percentage_error([integral_parameter_ref],[integral_parameter_sim])
            elif error_type == 'mse':
                error_i = mean_squared_error([integral_parameter_ref],[integral_parameter_sim])
            else: 
                raise NotImplemented(f'Error type {error_type} calculation not implemented')
        
            if integral_parameter in lda_dict.keys():
                lda = lda_dict[integral_parameter]
            else: lda = 1.0
            
            error_term += lda*error_i
                
        coefs = np.asarray(list(coef_dict.values()))
        defaults = np.asarray(list(coef_default_dict.values()))
        coef_term = np.mean(
            np.abs(
            np.divide( (coefs - defaults),
                  defaults)
            ))
        score = error_term*(1 + lda_dict['coef']*coef_term)
        print(f'error_term {error_term}')
        print(f'coef_term {coef_term}')
        print(f'score {score}')
        return score


    
"""
    def foam_mse_U_componentwise_2Dxy(self,foamtime,lda=1.0):
        self.foamtime = foamtime
        loss = mse_U_componentwise_2Dxy(U_ref=self.ref_df[['Ux','Uy']].values,
                                        U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                        )
        return loss
    
    def foam_mse_U_magnitude_2Dxy(self,foamtime,lda=1.0):
        self.foamtime = foamtime
        loss = mse_U_magnitude_2Dxy(U_ref=self.ref_df[['Ux','Uy']].values,
                                    U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                    )
        return loss
    
    def foam_multi_mse_U_magnitude_2Dxy_relcoeff_mean(self,foamtime,coeff_dict,coeff_default,lda=1.0):
        self.foamtime=foamtime
        loss = multi_mse_U_magnitude_2Dxy_relcoeff_mean(U_ref=self.ref_df[['Ux','Uy']].values,
                                                        U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                                        coeff_dict=coeff_dict,
                                                        coeff_default=coeff_default,
                                                        lda=lda)
        
        return loss
    
    def foam_multi_mape_U_magnitude_2Dxy_relcoeff_mean(self,foamtime,coeff_dict,coeff_default,lda=1.0):
        self.foamtime=foamtime
        loss = multi_mape_U_magnitude_2Dxy_relcoeff_mean(U_ref=self.ref_df[['Ux','Uy']].values,
                                                        U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                                        coeff_dict=coeff_dict,
                                                        coeff_default=coeff_default,
                                                        lda=lda)
        
        return loss
    
    def foam_multi_mape_U_magnitude_2Dxy_mape_k_relcoeff_mean(self,foamtime,coeff_dict,coeff_default,lda=1.0):
        self.foamtime=foamtime
        loss = multi_mape_U_magnitude_2Dxy_mape_k_relcoeff_mean(U_ref=self.ref_df[['Ux','Uy']].values,
                                                                U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                                                k_ref=self.ref_df['k'].values,
                                                                k_sim_mapped=self.map_to_reference('k'),
                                                                coeff_dict=coeff_dict,
                                                                coeff_default=coeff_default,
                                                                lda=lda)
        return loss
    
    def foam_multi_mape_U_magnitude_2Dxy_mape_k(self,foamtime):
        self.foamtime=foamtime
        loss = multi_mape_U_magnitude_2Dxy_mape_k(U_ref=self.ref_df[['Ux','Uy']].values,
                                                                U_sim_mapped=self.map_to_reference('U')[:,0:2],
                                                                k_ref=self.ref_df['k'].values,
                                                                k_sim_mapped=self.map_to_reference('k'),
                                                                )
        return loss
"""