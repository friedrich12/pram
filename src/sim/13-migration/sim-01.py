'''
A model of the interaction between conflict and migration.
'''

import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pram.data   import Probe
from pram.entity import Group, GroupQry, GroupSplitSpec, Site
from pram.rule   import IterAlways, TimeAlways, Rule, Noop
from pram.sim    import Simulation

import statistics


# ----------------------------------------------------------------------------------------------------------------------
class ConflictRule(Rule):
    """
    Conflict causes death and migration.  The probability of death scales with the conflict's severity and scale
    while the probability of migration scales with the conflict's scale only.  Multipliers for both factors are exposed
    as parameters.

    Time of exposure to conflict also increases the probability of death and migration, but that influence isn't
    modeled directly.  Instead, a proportion of every group of non-migrating agents can die or migrate at every step of
    the simulation.
    """

    def __init__(self, severity, scale, severity_death_mult=0.0001, scale_migration_mult=0.01, name='conflict', t=TimeAlways(), i=IterAlways()):
        super().__init__(name, t, i, group_qry=GroupQry(cond=[lambda g: g.has_attr({ 'is-migrating': False })]))

        self.severity = severity  # [0=benign .. 1=lethal]
        self.scale    = scale     # [0=contained .. 1=wide-spread]

        self.severity_death_mult  = severity_death_mult
        self.scale_migration_mult = scale_migration_mult

    def apply(self, pop, group, iter, t):
        p_death     = self.scale * self.severity * self.severity_death_mult
        p_migration = self.scale                 * self.scale_migration_mult

        return [
            GroupSplitSpec(p=p_death,     attr_set=Group.VOID),
            GroupSplitSpec(p=p_migration, attr_set={ 'is-migrating': True, 'migration-dur': 0 }),
            GroupSplitSpec(p=1 - p_death - p_migration)
        ]


# ----------------------------------------------------------------------------------------------------------------------
class MigrationRule(Rule):
    """
    Migrating population has a chance of dying and the probability of that happening is proportional to the harshness
    of the environment and the mass of already migrating population.  Multipliers for both factors are exposed as
    parameters.

    Time of exposure to the environment also increases the probability of death, but that influence isn't modeled
    directly.  Instead, a proportion of every group of migrating agents can die at every step of the simulation.

    Environmental harshness can be controled via another rule which conditions it on the time of year (e.g., winter
    can be harsher than summer or vice versa depending on region).
    """

    def __init__(self, env_harshness, env_harshness_death_mult=0.001, migration_death_mult=0.05, name='migration', t=TimeAlways(), i=IterAlways()):
        super().__init__(name, t, i, group_qry=GroupQry(cond=[lambda g: g.has_attr({ 'is-migrating': True })]))

        self.env_harshness = env_harshness  # [0=benign .. 1=harsh]

        self.env_harshness_death_mult = env_harshness_death_mult
        self.migration_death_mult     = migration_death_mult

    def apply(self, pop, group, iter, t):
        migrating_groups = pop.get_groups(GroupQry(cond=[lambda g: g.has_attr({ 'is-migrating': True })]))
        if migrating_groups and len(migrating_groups) > 0:
            migrating_m = sum([g.m for g in migrating_groups])
            migrating_p = migrating_m / pop.mass * 100
        else:
            migrating_p = 0

        p_death = min(self.env_harshness * self.env_harshness_death_mult + migrating_p * self.migration_death_mult, 1.00)

        return [
            GroupSplitSpec(p=p_death,     attr_set=Group.VOID),
            GroupSplitSpec(p=1 - p_death, attr_set={ 'migration-dur': group.get_attr('migration-dur') + 1 })
        ]


# ----------------------------------------------------------------------------------------------------------------------
class PopProbe(Probe):
    """ Prints a summary of the population at every iteration. """

    def __init__(self):
        super().__init__('pop')

    def run(self, iter, t):
        if iter is None:
            self.run_init()
        else:
            self.run_iter(iter, t)

    def run_init(self):
        self.pop_m_init = self.pop.mass

    def run_iter(self, iter, t):
        migrating_groups = self.pop.get_groups(GroupQry(cond=[lambda g: g.has_attr({ 'is-migrating': True })]))
        if migrating_groups and len(migrating_groups) > 0:
            migration_dur_lst = [g.get_attr('migration-dur') for g in migrating_groups]

            migrating_m        = sum([g.m for g in migrating_groups])
            migrating_p        = migrating_m / self.pop.mass * 100
            migrating_dur_mean = statistics.mean (migration_dur_lst)
            migrating_dur_sd   = statistics.stdev(migration_dur_lst) if len(migration_dur_lst) > 1 else 0
        else:
            migrating_m        = 0
            migrating_p        = 0
            migrating_dur_mean = 0
            migrating_dur_sd   = 0

        print(
            f'{iter or 0:>4}  ' +
            f'pop: {self.pop.mass:>9,.0f}    ' +
            f'dead: {self.pop.mass_out:>9,.0f}|{self.pop.mass_out / self.pop_m_init * 100:>3,.0f}%    ' +
            f'migrating: {migrating_m:>9,.0f}|{migrating_p:>3.0f}%    ' +
            f'migration-dur: {migrating_dur_mean:>6.2f} ({migrating_dur_sd:>6.2f})'
        )


# ----------------------------------------------------------------------------------------------------------------------
# Simulation:

s = (Simulation().
    set_pragmas(analyze=False, autocompact=True).
    add([
        ConflictRule(severity=0.05, scale=0.2),
        MigrationRule(env_harshness=0.05),
        PopProbe(),
        Group(m=1*1000*1000, attr={ 'is-migrating': False }),
    ]).
    run(48)  # months
)