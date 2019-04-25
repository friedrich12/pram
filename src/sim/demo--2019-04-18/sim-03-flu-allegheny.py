import os
import sys
from inspect import getsourcefile

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pram.data   import GroupSizeProbe, ProbeMsgMode, ProbePersistanceDB
from pram.entity import Group, GroupDBRelSpec, GroupQry, GroupSplitSpec, Site
from pram.rule   import Rule, TimeAlways
from pram.sim    import Simulation

from util.probes03 import probe_flu_at


import signal
def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


fpath_db = os.path.join(os.path.dirname(__file__), 'db', 'allegheny-students.sqlite3')


# ----------------------------------------------------------------------------------------------------------------------
# Rules are where machine reading will kick in over the summer.

class FluProgressRule(Rule):
    def __init__(self):
        super().__init__('flu-progress', TimeAlways())

    def apply(self, pop, group, iter, t):
        # Susceptible:
        if group.has_attr({ 'flu': 's' }):
            at  = group.get_rel(Site.AT)
            n   = at.get_pop_size()                               # total   population at current location
            n_e = at.get_pop_size(GroupQry(attr={ 'flu': 'e' }))  # exposed population at current location

            p_infection = float(n_e) / float(n)  # changes every iteration (i.e., the source of the simulation dynamics)

            return [
                GroupSplitSpec(p=    p_infection, attr_set={ 'flu': 'e' }),
                GroupSplitSpec(p=1 - p_infection, attr_set={ 'flu': 's' })
            ]

        # Exposed:
        if group.has_attr({ 'flu': 'e' }):
            return [
                GroupSplitSpec(p=0.2, attr_set={ 'flu': 'r' }),  # group size after: 20% of before (recovered)
                GroupSplitSpec(p=0.8, attr_set={ 'flu': 'e' })   # group size after: 80% of before (still exposed)
            ]

        # Recovered:
        if group.has_attr({ 'flu': 'r' }):
            return [
                GroupSplitSpec(p=0.9, attr_set={ 'flu': 'r' }),
                GroupSplitSpec(p=0.1, attr_set={ 'flu': 's' })
            ]


# ----------------------------------------------------------------------------------------------------------------------
class FluLocationRule(Rule):
    def __init__(self):
        super().__init__('flu-location', TimeAlways())

    def apply(self, pop, group, iter, t):
        # Exposed and low income:
        if group.has_attr({ 'flu': 'e', 'income': 'l' }):
            return [
                GroupSplitSpec(p=0.1, rel_set={ Site.AT: group.get_rel('home') }),
                GroupSplitSpec(p=0.9)
            ]

        # Exposed and medium income:
        if group.has_attr({ 'flu': 'e', 'income': 'm' }):
            return [
                GroupSplitSpec(p=0.6, rel_set={ Site.AT: group.get_rel('home') }),
                GroupSplitSpec(p=0.4)
            ]

        # Recovered:
        if group.has_attr({ 'flu': 'r' }):
            return [
                GroupSplitSpec(p=0.8, rel_set={ Site.AT: group.get_rel('school') }),
                GroupSplitSpec(p=0.2)
            ]

        return None


# ----------------------------------------------------------------------------------------------------------------------
# (1) Sites:

site_home = Site('home')
school_l  = Site(450149323)  # 88% low income students
school_m  = Site(450067740)  #  7% low income students


# ----------------------------------------------------------------------------------------------------------------------
# (2) Simulation:

def grp_setup(pop, group):
    return [
        GroupSplitSpec(p=0.9, attr_set={ 'flu': 's' }),
        GroupSplitSpec(p=0.1, attr_set={ 'flu': 'e' })
    ]


(Simulation().
    set().
        rand_seed(1928).
        pragma_autocompact(True).
        pragma_live_info(True).
        pragma_live_info_ts(False).
        done().
    add().
        rule(FluProgressRule()).
        rule(FluLocationRule()).
        probe(probe_flu_at(school_l, 'low-income')).  # the simulation output we care about and want monitored
        probe(probe_flu_at(school_m, 'med-income')).  # ^
        done().
    db(fpath_db).
        gen_groups(
            tbl      = 'students',
            attr_db  = [],
            rel_db   = [GroupDBRelSpec(name='school', col='school_id')],
            attr_fix = {},
            rel_fix  = { 'home': site_home },
            rel_at   = 'school'
        ).
        done().
    setup_groups(grp_setup).
    run(5)
)


# ----------------------------------------------------------------------------------------------------------------------
# Key points
#     Static rule analysis  - Automatically form groups based on rules
#     Dynamic rule analysis - Alert the modeler they might have missed something
#
# After 100 iterations
#     Low    income school - 24% of exposed kids
#     Medium income school - 14% of exposed kids