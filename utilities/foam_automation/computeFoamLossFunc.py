import os
import openfoamparser as Ofpp
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
#from utilities.foam_automation.interpolation import get_cell_centres, map_to_reference
from loss_functions.field import mse_U_componentwise_2Dxy, mse_U_magnitude_2Dxy, multi_mse_U_magnitude_2Dxy_relcoeff_mean, multi_mape_U_magnitude_2Dxy_relcoeff_mean, multi_mape_U_magnitude_2Dxy_mape_k_relcoeff_mean, multi_mape_U_magnitude_2Dxy_mape_k


class computeFoamFieldLossFunc():
    def __init__(self, foamdir, ref_df, interp_method='nearest'):
        self.foamdir=os.path.abspath(foamdir)
        self.ref_df=ref_df
        self.interp_method=interp_method
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
def mse_U_componentwise_2Dxy(foamdirectory = os.getcwd(),
             foamtime = None,
             ref_df = None,
             interp_method='linear'):
    foamdirectory = os.path.abspath(foamdirectory)
                           
    U_ref = ref_df[['Ux','Uy']].values
    mse = mean_squared_error(U_ref,U_sim_mapped)
    return mse

def mse_U_magnitude_2Dxy(foamdirectory = os.getcwd(),
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
"""