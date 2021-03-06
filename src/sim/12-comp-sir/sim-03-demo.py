'''
Multiple composite SIR models.

This is the simulation of two overlapping and time-unbounded SIR models, A and B.  Model B starts with a random time
delay and one of its parameters (gamma) random.  Additional gamma flu process is added as well to further demonstrate
how more complicated systems can be composed from modeling primitives.

This system uses time-invariant Markov chain solver to implement the SIR models.
'''

import matplotlib.pyplot as plt
import os

from dotmap import DotMap
from scipy.stats import truncnorm, uniform

from pram.entity      import Group, GroupSplitSpec
from pram.model.model import MCSolver
from pram.model.epi   import SIRSModel
from pram.rule        import ODESystemMass, GammaDistributionProcess
from pram.sim         import Simulation
from pram.traj        import ClusterInf, Trajectory, TrajectoryEnsemble


# ----------------------------------------------------------------------------------------------------------------------
fpath_db = os.path.join(os.path.dirname(__file__), 'data', 'sir-comp-demo.sqlite3')


# ----------------------------------------------------------------------------------------------------------------------
# Helper functions (to simplify the code below):

def U(a,b, n=None):
    return uniform(a,a+b).rvs(n)

def TN(a,b, mu, sigma, n=None):
    return truncnorm((a - mu) / sigma, (b - mu) / sigma, mu, sigma).rvs(n)

group_names = [
    (0, 'S', Group.gen_hash(attr={ 'flu': 's' })),
    (1, 'I', Group.gen_hash(attr={ 'flu': 'i' })),
    (2, 'R', Group.gen_hash(attr={ 'flu': 'r' }))
]


# ----------------------------------------------------------------------------------------------------------------------
# A gamma distribution process rule:

class MakeSusceptibleProcess(GammaDistributionProcess):  # extends the GammaDistributionProcess primitive
    def apply(self, pop, group, iter, t):
        p = self.get_p(iter)
        return [
            GroupSplitSpec(p=p, attr_set={ 'flu': 's' }),
            GroupSplitSpec(p=1-p)
        ]

    def is_applicable(self, group, iter, t):
        return super().is_applicable(group, iter, t) and group.has_attr({ 'flu': 'r' })


# ----------------------------------------------------------------------------------------------------------------------
# Simulations:

if os.path.isfile(fpath_db): os.remove(fpath_db)

# te = TrajectoryEnsemble(fpath_db)
# te = TrajectoryEnsemble(fpath_db, cluster_inf=ClusterInf(address='auto'))
te = TrajectoryEnsemble(fpath_db, cluster_inf=ClusterInf(num_cpus=6, memory=500*1024*1024, object_store_memory=500*1024*1024, include_webui=False))

if te.is_db_empty:  # generate simulation data if the trajectory ensemble database is empty
    te.set_pragma_memoize_group_ids(True)
    te.add_trajectories([
        (Simulation().
            add([
                SIRSModel('flu', beta=0.10, gamma=0.05,          solver=MCSolver()),                                   # model 1
                SIRSModel('flu', beta=0.50, gamma=U(0.01, 0.15), solver=MCSolver(), i=[int(5 + TN(0,50, 5,10)), 50]),  # model 2
                MakeSusceptibleProcess(i=[50,0], a=3.0, scale=flu_proc_scale),                                         # model 3
                Group(m=1000, attr={ 'flu': 's' })
            ])
        ) for flu_proc_scale in U(1,5, 20)  # a 20-trajectory ensemble
    ])
    te.set_group_names(group_names)
    te.run(120)

te.plot_mass_locus_line     ((1200,300), os.path.join(os.path.dirname(__file__), 'out', '_plot-line.png'), opacity_min=0.2)
te.plot_mass_locus_line_aggr((1200,300), os.path.join(os.path.dirname(__file__), 'out', '_plot-iqr.png'))

# fpath_diag = os.path.join(os.path.dirname(__file__), 'out', 'sim-03.diag')
# fpath_pdf  = os.path.join(os.path.dirname(__file__), 'out', 'sim-03.pdf')
# te.traj[2].sim.gen_diagram(fpath_diag, fpath_pdf)
