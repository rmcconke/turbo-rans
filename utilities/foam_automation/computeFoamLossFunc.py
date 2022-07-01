import os
import openfoamparser as Ofpp
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pandas as pd
from loss_functions.GEDCP import gedcp

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
        df = pd.read_csv(os.path.join(self.foamdir,'postProcessing/forceCoeffs1/0/coefficient_0.dat'),delimiter ='\t',skiprows = 12)
        df.columns = df.columns.str.replace(' ', '')
        return float(df[coef_name].iloc[-1])
        
    def foam_gedcp(self, foamtime,
                                     coef_default_dict,
                                     coef_dict,
                                     error_calc_fields,
                                     error_calc_intparams,
                                     lda_dict={'coef': 0.5},
                                     error_type = 'mape'):
        """
        Foam interface for GEDCP loss function in loss_functions
        """
        
        self.foamtime = foamtime
        
        field_sim_mapped_dict = dict.fromkeys(error_calc_fields)
        field_ref_dict = dict.fromkeys(error_calc_fields)
        integral_param_sim_dict = dict.fromkeys(error_calc_intparams)
        integral_param_ref_dict = dict.fromkeys(error_calc_intparams)
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
                
            field_sim_mapped_dict[field] = field_sim_mapped
            field_ref_dict[field] = field_ref
            
        for integral_parameter in error_calc_intparams:
            if integral_parameter == 'Cl':
                integral_parameter_ref = float(self.ref_df[integral_parameter][0])
                integral_parameter_sim = self.read_force_coefficient('Cl')
            elif integral_parameter == 'Cd':
                integral_parameter_ref = self.ref_df[integral_parameter][0]
                integral_parameter_sim = self.read_force_coefficient('Cd')
            else:
                raise NotImplemented(f'Int. parameter {integral_parameter} error calculation not implemented')   

            integral_param_sim_dict[integral_parameter] = integral_parameter_sim
            integral_param_ref_dict[integral_parameter] = integral_parameter_ref
        
        score = gedcp(field_sim_mapped_dict = field_sim_mapped_dict,
                      field_ref_dict = field_ref_dict,
                      integral_param_sim_dict = integral_param_sim_dict,
                      integral_param_ref_dict = integral_param_ref_dict,
                      coef_default_dict = coef_default_dict,
                      coef_dict = coef_dict,
                      lda_dict = {'coef': 0.5},
                      error_type = 'mape')
        return score
