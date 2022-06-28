import os

def optimize_foam_case(n_iter = 30,
                       n_points_sampled = 4,
                       foamdir=os.get_cwd(),
                       savedir=os.path.join(os.get_cwd(),'optimal'),
                    ):