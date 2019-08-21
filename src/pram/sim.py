# PRAMs - Probabilitistic Relational Agent-based Models
#
# BSD 3-Clause License
#
# Copyright (c) 2018-2019, momacs, University of Pittsburgh
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Contributors
#     Paul R Cohen                                                                                    [2018.10.01 - ...]
#         The idea of PRAMs
#         The original implementation (not available here)
#     Tomek D Loboda  (https://github.com/ubiq-x)                                                     [2018.12.16 - ...]
#         The original author of the present design and implementation
#
# ----------------------------------------------------------------------------------------------------------------------
#
# TODO
#     Quick
#         Sync sim.Timer with rule.Time
#         Associate time with rules, not simulations
#         Associate the output database (or a directory) with a simulation, not probe persistance
#         - Store school info (e.g., size) in the probe DB and associate with the probes
#         - Allow simulation to output warning to a file or a database
#         - Abstract the single-group group splitting mechanism as a dedicated method.  Currently, that is used in
#           ResetDayRule.apply() and AttendSchoolRule.setup() methods.
#         Allow executing rule sets in the order provided
#             E.g., some rules need to be run after all others have been applied
#             This may not be what we want because the idea of PRAMs is to avoid order effects.
#         - Antagonistic rules (e.g., GoHome and GoToWork), if applied at the same time will always result in order
#           effects, won't they? Think about that.
#         - It is possible to have groups with identical names.  If we wanted to disallow that, the best place to do
#           that in is GroupPopulation.add_group().
#         Abastract Group.commit() up a level in the hierarchy, to Entity, which will benefit Site.
#         Abstract hashing up to Entity.
#         - Consider making attribute and relation values objects.  This way they could hold an object and its hash
#           which could allow for more robust copying.
#     Paradigm shift
#         Implement everything on top of a relational database
#     Internal mechanics
#         Simulation timer
#             Return actual time (i.e., implement flexible looping mechanism)
#             Specify time display format that's complementary to but independent of the simulation timer
#             Remove Simulation.set_iter_cnt and Simulation.set_time
#         Population mass
#             Allow the population mass to grow or shrink, most likely only via rules.
#         Group querying
#             Implement a more flexible way to query groups (GroupPopulation.get_groups())
#             - Ideally, we would want to use popular query languages, SQL being the prime example of one.  Because
#               PRAM is a simulation framework, extensions to SQL might be in order (e.g., to account for the passage
#               of time; SELECT a FROM b AT t=3)
#         Group size
#             - Should we allow fractional group sizes?  At first glance it might make little sense to have a group of
#               500.38 agents, but it's possible that if we don't allow that agents will be "slipping" between groups
#               in a hard-to-control manner.  Perhaps floating-point arithmetic is the way to go given that we can
#               always round but not vice versa.
#               * Current solution: allow floating-point group size
#         Timer-based group states
#             - Add group states that respond to the passage of time and are part of a mechanism.  For example,
#               'flu-asympt-time' could be a count-down attribute that determines for how long the group stays
#               asymptomatic before it turns symptomatic.  At some point, portion by portion, the population of
#               infected but asymptomatic agents would become symptomatic.  In that respect, a presense of a time-based
#               state would imply a time-based rule that needed to be aplied at some point (possibly conditionally).
#         Efficient group management
#             1. GroupPopulation class [DONE]
#             2. Move to frozen hash tables whenever possible (for runtime safety and performance)
#                    frozendict
#                        https://pypi.org/project/frozendict
#                    frozenmap
#                        https://pypi.org/project/frozenmap
#         Account for time
#             Generate unique entity run-time IDs
#             Scale probabilities with time
#                 1. Add process length and use it to scale group-splitting probabilities (i.e., those used by rules)
#                 2. Add cooldown to a rule; the rule does not fire until the cooldown is over; reset cooldown.
#             Option 2 appears more palatable at the moment, at least to me
#         Account for space and spacial proximity
#             - Are xy- or geo-coordinates necessary?  Perhaps relations can handle this already.  For example, a
#               group of agents already shares the same location so we know they are in proximy of one another.
#               Moreover, if we knew how many agents work or shop at a particular location, we would know that number
#               of agents will form a group based on location.  Perhaps it would be enough for a Site (e.g., a store)
#               and a Resource (e.g., a public bus) to have a capacity property.
#         Convert between list of agents and groups
#             This should be a natural way of enabling FRED-PRAM interoperability
#             In a more general sense, this would enable parallel runs comparisons between ABMs, PRAMs, etc.
#         Representational expressiveness
#             - Move from discrete models (i.e., those implying states) to continuous or hybrid models (i.e., those
#               implying equations)
#         Type safety
#             Use static type checking
#                 https://medium.com/@ageitgey/learn-how-to-use-static-type-checking-in-python-3-6-in-10-minutes-12c86d72677b
#             Add type checks
#         Optimization (when the time comes, but not later)
#             Move to PyPy
#             Memoize GroupQry queries
#                 They should be reset (or handled inteligently) after mass transfer
#             Persist probe results on a batch basis (e.g., via 'executemany()')
#             Remove groups unused in certain number of simulation steps to account for high group-dynamic scenarios
#     Simulation construction
#         Generate from DB
#             - Make sure groups of students and workers are generated properly from one Simulation.gen_groups_from_db()
#               call.
#             - How to automatically inject relations from the static analysis into the DB generation in
#               Simulation.gen_groups_from_db()?
#             Generate groups (and therefore sites) from multiple tables
#             Generate groups (and therefore sites) from multiple databases
#         Define simulation definition language
#             - Provide probabilities as a transition matrix.  Perhaps the entire simulation could be specified as a
#               Bayesian network which would naturally imply a conditional probability distributions (or densities).
#         Define simulation based on a relational database
#         Hand-drawn input
#             Implement a UI that turns hand-drawn graphs into PRAM simulations
#             Possible approaches
#                 Image moments
#             Quick literature search
#                 https://www.researchgate.net/publication/302980429_Hand_Drawn_Optical_Circuit_Recognition
#                 http://homepages.inf.ed.ac.uk/thospeda/papers/yu2016sketchanet.pdf
#                 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5578632/
#                 http://cs231n.stanford.edu/reports/2017/pdfs/420.pdf
#                 DeepSketch2
#                     https://www.semanticscholar.org/paper/DeepSketch-2%3A-Deep-convolutional-neural-networks-Dupont-Seddati/feac7ae2ce66e6dcc8e8c64223dc5624edea8d08
#     Visualization and UI
#         Visualize simulations
#         Make the visualization controlable (ideally MVC)
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Milestones: Environment
#     Development started (Python 3.6.1; MacOS 10.12.6)                                        [2018.12.16]
#     GitHub repository created                                                                [2019.01.18]
#     Ported to FreeBSD (Python 3._._; 12.0R)                                                  []
#     Ported to Ubuntu (Python 3._._; 18.04 LTS)                                               []
#     Moved to PyPy                                                                            []
#     Published to PyPI                                                                        []
#     Containerized                                                                            []
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Milestones: Code
#     Simulation
#         c Simulation class                                                                   [2018.12.16 - 2019.07.19]
#         Timer
#             c Timer                                                                          [2019.03.31]
#             c Timer (simple subclasses, e.g., HourTimer)                                     [2019.03.31 - 2019.04.03]
#             c CalDayTimer                                                                    [2019.03.31 - ...]
#             c CalMonthTimer                                                                  [2019.03.31 - ...]
#         c SimulationAdder                                                                    [2019.04.06]
#         c SimulationSetter                                                                   [2019.04.06]
#         c SimulationDBI                                                                      [2019.04.22]
#         c SimulationPlotter                                                                  [2019.04.10]
#         c StaticRuleAnalyzer                                                                 [2019.03.02 - 2019.04.14]
#         c DynamicRuleAnalyzer                                                                [2019.03.02 - 2019.05.04]
#         c Trajectory                                                                         [2019.07.12 - 2019.07.29]
#         c TrajectoryEnsemble                                                                 [2019.07.12 - 2019.07.29]
#         Entities
#             c Agent                                                                          [2018.12.16 - 2019.01.05]
#             c Entity                                                                         [2018.12.16 - 2019.03.22]
#             c Group                                                                          [2019.12.16 - 2019.03.10]
#                 f Splitting                                                                  [2019.01.04 - 2019.02.11]
#                 f Freezing                                                                   [2019.03.09]
#                 f DB generation                                                              [2019.02.20 - 2019.04.28]
#             c GroupDBRelSpec                                                                 [2019.02.20]
#             c GroupQry                                                                       [2019.01.12 - 2019.01.21]
#             c GroupSplitSpec                                                                 [2019.01.06 - 2019.01.21]
#             c Resource                                                                       [2010.01.18 - 2019.03.21]
#             c Site                                                                           [2018.12.16 - 2019.03.21]
#                 f DB generation                                                              [2019.02.20 - 2019.03.22]
#         Rules
#             Time
#                 c Time                                                                       [2019.01.06]
#                 c TimeAlways                                                                 [2019.03.31]
#                 c TimePoint                                                                  [2019.01.22]
#                 c TimeInterval                                                               [2019.01.06]
#             Basic
#                 c Rule                                                                       [2019.01.03 - 2019.03.31]
#                 c GoToRule                                                                   [2019.01.21 - 2019.03.27]
#                 c GoToAndBackTimeAtRule                                                      [2019.01.22 - 2019.03.27]
#                 c ResetRule                                                                  [2019.01.23 - 2019.03.27]
#                 c ResetSchoolDayRule                                                         [2019.01.23 - 2019.03.27]
#                 c ResetWorkDayRule                                                           [2019.01.23 - 2019.03.27]
#             Epidemiology
#                 c ProgressFluRule (deprecated)                                               [2019.01.03 - 2019.03.31]
#                 c ProgressAndTransmitFluRule (deprecated)                                    [2019.02.05 - 2019.03.11]
#                 c SEIRRule                                                                   [2019.03.25 - 2019.04.06]
#                 c SEIRFluRule                                                                [2019.04.06 - 2019.04.08]
#             f Setup                                                                          [2019.01.23]
#         Population
#             c Population                                                                     [2019.01.07]
#             c AgentPopulation                                                                [2019.01.07]
#             c GroupPopulation                                                                [2019.01.07 - 2019.07.15]
#                 f Selecting groups                                                           [2019.01.07 - 2019.01.21]
#                 f Rule application                                                           [2019.01.04 - 2019.01.17]
#                 f Mass transfer                                                              [2019.01.04 - 2019.02.24]
#             c MassFlowGraph                                                                  [2019.07.26 - ...]
#
#     Data collection
#         c Probe                                                                              [2019.01.18 - 2019.03.31]
#         c ProbePersistanceDB                                                                 [2019.03.02 - 2019.03.18]
#         c ProbePersistanceFS                                                                 [2019.03.02]
#         c GroupSizeProbe                                                                     [2019.01.18 - 2019.07.15]
#
#     Logging
#         c Log                                                                                [2019.01.06]
#         c LogMan                                                                             [2019.01.06]
#
#     Communication and control
#         c TCPServer                                                                          []
#         c TCPClient                                                                          []
#         c HTTPServer                                                                         []
#         s Protocol                                                                           []
#
#     Tests
#         c GroupTestCase                                                                      [2019.01.11]
#         c SimulationTestCase                                                                 [2019.01.19]
#         c SiteTestCase                                                                       [2019.01.21]
#         c RuleAnalyzerTestCase                                                               [2019.03.18]
#
#     Visualization and UI
#         l WebUI                                                                              [2019.04.02 - 2019.06.10]
#
#     Utilities
#         c Data                                                                               [2019.01.06]
#         c DB                                                                                 [2019.02.11 - 2019.03.18]
#         c Err                                                                                [2019.01.21]
#         c FS                                                                                 [2019.01.06 - 2019.03.22]
#         c Hash                                                                               [2019.01.06]
#         c MPCounter                                                                          [2019.01.06]
#         c Size                                                                               [2019.01.06 - 2019.02.11]
#         c Str                                                                                [2019.01.06]
#         c Tee                                                                                [2019.01.06]
#         c Time                                                                               [2019.01.06 - 2019.04.01]
#
#     Optimization
#         String interning (sys.intern; not needed in Python 3)                                [2019.01.06 - 2019.01.17]
#         __slots__                                                                            [2019.01.17]
#         Profiling
#             ProbePersistanceDB                                                               [2019.03.16 - 2019.03.17]
#
#     Legend
#         c Class
#         f Functionality
#         l Layer
#         s Specification
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Philosophical issues
#     Dynamical system
#         Dynamical system use differential equations as a state-and-space model.  It would be interesting to
#         investigate if a similar approach would be viable here.  Perhaps an end-to-end differentible system is
#         possible.  I suspect, however, it wouldn't, mostly on the grounds of computational intractability for
#         larger simulations.
#     State-space models
#         In a more general sense, how does PRAM correpond to state-space models?
#     Logistic map
#         [2019.01]
#         My early and simple simulations resulted with the population distribution reaching what appears to be some
#         sort of a stationary distribution.  That convergence was rather fast (around 20 time steps) and while I don't
#         know what's driving it, I wonder if it's in any way related to the logistic map:
#
#             x_{n+1} = r x_n (1-x_n)
#
#         If there is a connection, perhaps it can be described with polynomial mapping of degree higher than two.  I'm
#         not sure how to visualize those higher dimensions.
#
#         [2019.01]
#         Having thought of this a tiny bit more, I started to question my initial intuition because the logistic
#         function models population size change (i.e., growth or decline) and not distribution.  Perhaps it would
#         still apply to subpopulation... not sure.
#
#         [2019.02.07]
#         I am now almost certain that I was wrong all along.  I think that the observed convergence is that of a
#         time-homogenous Markov chain with a finite state space tending to its stationary distribution \pi:
#
#             \pi = \pi P,
#
#         where $P$ is the chain's transition probability matrix.  While the flu progression simulation is equivalent
#         to such a Markov chain, more complicated simulations (e.g., the flu transmission model) won't reduce to
#         stationary chains.
#     Evaluation of PRAM
#         Historical data
#             - Use the initial state given by historical data to seed a PRAM simulation.  Compare how short of the
#              rest of the data the simulation is at specific milestone points.
#             - Additionally, historical data could be used to infer the rules.
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Simulation ideas
#     Smoking effects on lifespan
#         Groups will have an attribute 'lifespan'
#         Rule will make a portion of groups smoke
#         Smoking (both active and passive smoking) will (diffrentially) negatively impact lifespan
#         Being in the proximity of other smokers will increase likelihood of smoking
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Resources: Development
#     Simulations
#         SimPy
#             Discrete event simulation for Python
#             https://simpy.readthedocs.io
#
#     Agent-based modeling
#         Mesa
#             https://mesa.readthedocs.io/en/latest/index.html
#
#     Data structures
#         collections
#             https://docs.python.org/3.6/library/collections.html
#         Time Complexity
#             https://wiki.python.org/moin/TimeComplexity
#         attrs
#             More memory-efficient and more feature-rich than property classes or the 'namedtuple' data type
#             https://www.attrs.org
#
#     Multithreading
#         Stackless
#             https://github.com/stackless-dev/stackless/wiki
#             http://doc.pypy.org/en/latest/stackless.html
#
#     Multiprocessing
#         multiprocessing
#             Process-based parallelism
#             https://docs.python.org/3.6/library/multiprocessing.html
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Resources: Statistics
#     Sampling
#         How to get embarrassingly fast random subset sampling with Python
#             https://medium.freecodecamp.org/how-to-get-embarrassingly-fast-random-subset-sampling-with-python-da9b27d494d9
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Resources: Publishing
#     Bayesian Nets plate notation graphs
#         LaTeX
#             https://github.com/jluttine/tikz-bayesnet
#         Python
#             http://daft-pgm.org
#     Graphs
#         http://www.graphviz.org
#         http://latexdraw.sourceforge.net
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Resources: Other
#     ...
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Deployment: MacOS  (Python 3.6.1)
#     dir=...
#
#     if [ $(which brew | wc -l | bc) == 0 ]
#     then/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
#     else brew update
#     fi
#
#     brew install git python3
#
#     [ -d $dir ] && echo "Directory already exists" && exit 1
#     python -m venv $dir && cd $dir
#     source ./bin/activate
#
#     pip install --upgrade pip && easy_install -U pip
#
#     python -m pip install numpy attrs
#
#     git clone https://github.com/momacs/pram
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Deployment: FreeBSD  (12.0R, Python 3.6._)
#         ...
#
# ----------------------------------------------------------------------------------------------------------------------
#
# Deployment: Ubuntu  (18.04 LTS, Python 3.6._)
#         ...
#
# ----------------------------------------------------------------------------------------------------------------------

import ast
import bz2
import datetime
import gc
import gzip
import inspect
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import random
import sqlite3

from collections import namedtuple, Counter
from dotmap      import DotMap
from scipy.stats import gaussian_kde

from .data   import GroupSizeProbe, Probe
from .entity import Agent, Group, GroupQry, Site
from .pop    import GroupPopulation
from .rule   import Rule
from .util   import Err, FS, Time


# ----------------------------------------------------------------------------------------------------------------------
class SimulationConstructionError(Exception): pass
class SimulationConstructionWarning(Warning): pass


# ----------------------------------------------------------------------------------------------------------------------
class Timer(object):
    '''
    Simulation timer.

    This discrete time is unitless; it is the simulation context that defines the appropriate granularity.  For
    instance, million years (myr) might be appropriate for geological processes while Plank time might be appropriate
    for modeling quantum phenomena.  For example, one interpretation of 'self.t == 4' is that the current simulation
    time is 4am.

    To enable natural blending of rules that operate on different time scales, the number of milliseconds is stored by
    the object.  Because of this, rule times, which define the number of milliseconds in a time unit, can be scaled.

    Apart from time, this timers also stores the iteration count.
    '''

    # TODO: Loop detection currently relies on modulus which does not handle 'step_size' > 1 properly.

    POSIX_DT = datetime.datetime(1970, 1, 1)  # POSIX datetime

    def __init__(self, ms=Time.MS.ms, iter=float('inf'), t0=0, tmin=0, tmax=10, do_disp_zero=True):
        self.ms = ms
        self.i_max = iter
        self.i = None  # set by reset()

        self.t0 = t0         # how time is going to be diplayed
        self.tmin = tmin     # ^
        self.tmax = tmax     # ^
        self.t = t0          # ^
        self.t_loop_cnt = 0  # ^

        self.last_iter_t0 = None
        self.last_iter_t1 = None
        self.last_iter_t  = None

        self.is_running = False

        if self.tmin > self.tmax:
            raise TypeError(f'The min time has to be smaller than the max time.')

        self.do_disp_zero = do_disp_zero  # flag: print empty line on zero?

        self.did_loop_on_last_iter = False  # flag: keeping this avoids printing looping info right before the simulation ends

        self.reset()

    def __repr__(self):
        return '{}(name={}, ms={}  iter={}))'.format(self.__class__.__name__, self.ms, self.i_max)

    def __str__(self):
        return '{}'.format(self.__class__.__name__, self.ms, self.i_max)

    def add_dur(self, dur):
        self.i_max += math.floor(dur / self.ms)

    def add_iter(self, iter):
        self.i_max += iter

    @staticmethod
    def by_ms(ms, **kwargs):
        ''' Returns a Timer object which matched the specified number of milliseconds. '''

        timer = {
            Time.MS.m  : MilsecTimer,
            Time.MS.s  : SecTimer,
            Time.MS.m  : MinTimer,
            Time.MS.h  : HourTimer,
            Time.MS.d  : DayTimer,
            Time.MS.w  : WeekTimer,
            Time.MS.M  : MonthTimer,
            Time.MS.y  : YearTimer
        }.get(ms, None)
        if not timer:
            raise ValueError(f'No timer associated with time unit given by the number of milliseconds: {ms}')
        return timer(**kwargs)

    def get_i(self):
        return self.i

    def get_t(self):
        return self.t

    def get_t_loop_cnt(self):
        return self.t_loop_cnt

    def get_i_left(self):
        return self.i_max - self.i

    def get_t_left(self):
        return self.i_max - self.i

    @staticmethod
    def get_ts():
        return (datetime.datetime.now() - Timer.POSIX_DT).total_seconds() * 1000  # [ms]

    def reset(self):
        self.i = 0
        self.t = self.t0
        self.t_loop_cnt = 0

    def set_dur(self, dur):
        self.i_max = math.floor(dur / self.ms)

    def set_iter(self, iter):
        self.i_max = iter

    def start(self):
        self.is_running = True
        self.last_iter_t0 = Timer.get_ts()

    def step(self):
        self.i += 1
        if self.i > self.i_max:
            self.i = self.i_max
            raise TypeError(f'Timer has reached the maximum value of {self.tmax}.')

        self.t = self.i % self.tmax + self.tmin

        if self.do_disp_zero and self.did_loop_on_last_iter:
            # print(f'\nLoop: {self.t_loop_cnt + 1}')
            self.did_loop_on_last_iter = False

        if self.i > 0 and self.t == self.tmin:
            self.t_loop_cnt += 1
            self.did_loop_on_last_iter = True

        self.last_iter_t1 = Timer.get_ts()
        self.last_iter_t  = self.last_iter_t1 - self.last_iter_t0
        self.last_iter_t0 = Timer.get_ts()
        self.last_iter_t1 = None

    def stop(self):
        self.last_iter_t1 = Timer.get_ts()
        self.last_iter_t  = self.last_iter_t1 - self.last_iter_t0
        self.is_running = False


# ----------------------------------------------------------------------------------------------------------------------
class MilsecTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.ms, iter, 0, 0, 1000, do_disp_zero)


class SecTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.s, iter, 0, 0, 60, do_disp_zero)


class MinTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.m, iter, 0, 0, 60, do_disp_zero)


class HourTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.h, iter, 0, 0, 24, do_disp_zero)


class DayTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.d, iter, 0, 0, 365, do_disp_zero)


class WeekTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.w, iter, 0, 0, 52, do_disp_zero)


class MonthTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.M, iter, 0, 0, 12, do_disp_zero)


class YearTimer(Timer):
    def __init__(self, iter=float('inf'), do_disp_zero=True):
        super().__init__(Time.MS.y, iter, 0, 2000, 10000, do_disp_zero)


# ----------------------------------------------------------------------------------------------------------------------
# class CalMonthTimer(Timer):


# ----------------------------------------------------------------------------------------------------------------------
# class CalDayTimer(Timer):


# ----------------------------------------------------------------------------------------------------------------------
class DynamicRuleAnalyzer(object):
    '''
    Analyze rule conditioning after running the simulation.  This is done by processing group attributes and
    relations that the simulation has recorded as accessed by at least one rule.  The evidence of attributes and
    relations having been actually accessed is a strong one.  However, as tempting as it may be to use this
    information to prune groups, it's possible that further simulation iterations depend on other sets of
    attributes and relations.  As a consequence, it is not possible to perform error-free groups auto-pruning based
    on this analysis alone.

    The sets of attributes and relations used (i.e., conditioned on by at least one rule) are not cleared between
    simulation runs, only updated.  This way a simulation will always be aware of what was relevant from the very
    beginning.  This information will also be persisted if the simulation object is serialized to continue
    execution on another system.
    '''

    def __init__(self, sim):
        self.sim = sim

        self.attr_used = set()
        self.rel_used  = set()

        self.attr_unused = set()
        self.rel_unused  = set()

    def analyze(self):
        # Get attributes and relations that define groups:
        self.attr_groups = set()
        self.rel_groups  = set()
        for g in self.sim.pop.groups.values():
            for ga in g.attr.keys(): self.attr_groups.add(ga)
            for gr in g.rel.keys():  self.rel_groups. add(gr)

        # Update the set of used (i.e., conditioned on by at least one rule) attributes and relations:
        # self.attr_used.update(getattr(Group, 'attr_used').copy())
        # self.rel_used.update(getattr(Group, 'rel_used').copy())
        self.attr_used.update(getattr(Group, 'attr_used'))
        self.rel_used.update(getattr(Group, 'rel_used'))

        # Do a set-subtraction to get attributes and relations not conditioned on by even one rule:
        self.attr_unused = self.attr_groups - self.attr_used
        self.rel_unused  = self.rel_groups  - self.rel_used


# ----------------------------------------------------------------------------------------------------------------------
class StaticRuleAnalyzer(object):
    '''
    Analyzes the syntax (i.e., abstract syntax trees or ASTs) of rule objects to identify group attributes and
    relations these rules condition on.

    Apart from attempting to deduce the attributes and rules, this class keeps track of the numbers of recognized and
    unrecognized attributes and relations (compartmentalized by method type, e.g., 'has_attr' and 'get_attr').

    References
        https://docs.python.org/3.6/library/dis.html
        https://docs.python.org/3.6/library/inspect.html
        https://docs.python.org/3.6/library/ast.html

        https://github.com/hchasestevens/astpath
        https://astsearch.readthedocs.io/en/latest

    # TODO: Double check the case of multiple sequential simulation runs.
    '''

    def __init__(self):
        self.reset()

    def _dump(self, node, annotate_fields=True, include_attributes=False, indent='  '):
        '''
        Source: https://bitbucket.org/takluyver/greentreesnakes/src/default/astpp.py?fileviewer=file-view-default
        '''

        if not isinstance(node, ast.AST):
            raise TypeError('expected AST, got %r' % node.__class__.__name__)
        return self._format(node, 0, annotate_fields, include_attributes, indent)

    def _format(self, node, level=0, annotate_fields=True, include_attributes=False, indent='  '):
        '''
        Source: https://bitbucket.org/takluyver/greentreesnakes/src/default/astpp.py?fileviewer=file-view-default
        '''

        if isinstance(node, ast.AST):
            fields = [(a, self._format(b, level, annotate_fields, include_attributes, indent)) for a, b in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, self._format(getattr(node, a), level, annotate_fields, include_attributes, indent))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + self._format(x, level + 2, annotate_fields, include_attributes, indent) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)

    def _analyze_test(self, node):
        if isinstance(node, ast.AST):
            fields = [(a, self._analyze_test(b)) for a,b in ast.iter_fields(node)]
            return ''.join([node.__class__.__name__, '(', ', '.join((b for a,b in fields)), ')'])
        elif isinstance(node, list):
            lines = []
            lines.extend((self._analyze_test(x) + ',' for x in node))
            return '\n'.join(lines)
        return repr(node)

    def _analyze(self, node):
        '''
        Processe a node of the AST recursively looking for method calls that suggest group attribute and relation names
        conditioned on by the rule.  It also updates counts of all known and unknown names (compartmentalized by the
        method name).

        References
            https://docs.python.org/3.6/library/ast.html#abstract-grammar
        '''

        if isinstance(node, ast.AST):
            for _,v in ast.iter_fields(node):
                self._analyze(v)

            if node.__class__.__name__ == 'Call':
                call_args = list(ast.iter_fields(node))[1][1]

                if list(ast.iter_fields(node))[0][1].__class__.__name__ == 'Attribute':
                    attr = list(ast.iter_fields(node))[0][1]
                    attr_name = list(ast.iter_fields(attr))[1][1]

                    if attr_name in ('get_attr', 'get_rel', 'has_attr', 'has_rel', 'ga', 'gr', 'ha', 'hr'):
                        call_args = call_args[0]
                        if call_args.__class__.__name__ == 'Str':
                            if attr_name in ('get_attr', 'has_attr', 'ga', 'ha'):
                                self.attr_used.add(StaticRuleAnalyzer.get_str(call_args))
                            else:
                                self.rel_used.add(StaticRuleAnalyzer.get_str(call_args))
                            self.cnt_rec[attr_name] += 1
                        elif call_args.__class__.__name__ in ('List', 'Dict'):
                            for i in list(ast.iter_fields(call_args))[0][1]:
                                if i.__class__.__name__ == 'Str':
                                    if attr_name in ('get_attr', 'has_attr', 'ga', 'ha'):
                                        self.attr_used.add(StaticRuleAnalyzer.get_str(i))
                                    else:
                                        self.rel_used.add(StaticRuleAnalyzer.get_str(i))
                                    self.cnt_rec[attr_name] += 1
                                else:
                                    self.cnt_unrec[attr_name] += 1
                                    # print(list(ast.iter_fields(i)))
        elif isinstance(node, list):
            for i in node:
                self._analyze(i)

    def analyze_rules(self, rules):
        ''' Can be (and in fact is) called before any groups have been added. '''

        # (1) Reset the state:
        self.attr_used = set()
        self.rel_used  = set()

        self.attr_unused = set()
        self.rel_unused  = set()

        self.cnt_rec   = Counter({ 'get_attr': 0, 'get_rel': 0, 'has_attr': 0, 'has_rel': 0 })  # recognized
        self.cnt_unrec = Counter({ 'get_attr': 0, 'get_rel': 0, 'has_attr': 0, 'has_rel': 0 })  # unrecognized

        # (2) Analyze the rules:
        for r in rules:
            self.analyze_rule(r)

        self.are_rules_done = True

    def analyze_groups(self, groups):
        ''' Should be called after all the groups have been added. '''

        attr_groups = set()  # attributes defining groups
        rel_groups  = set()  # ^ (relations)
        for g in groups:
            for ga in g.attr.keys(): attr_groups.add(ga)
            for gr in g.rel.keys():  rel_groups. add(gr)

        self.attr_unused = attr_groups - self.attr_used  # attributes not conditioned on by even one rule
        self.rel_unused  = rel_groups  - self.rel_used   # ^ (relations)

        self.are_groups_done = True

    def analyze_rule(self, rule):
        tree = ast.fix_missing_locations(ast.parse(inspect.getsource(rule.__class__)))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef): continue  # skip non-classes

            for node_fn in node.body:
                if not isinstance(node_fn, ast.FunctionDef): continue  # skip non-methods
                self._analyze(node_fn.body)

                # if node_fn.name in ('is_applicable'): print(self._analyze_01(node_fn.body))

    def dump(self, rule):
        tree = ast.fix_missing_locations(ast.parse(inspect.getsource(rule.__class__)))
        print(self._dump(tree))

    @staticmethod
    def get_str(node):
        return list(ast.iter_fields(node))[0][1]

    def reset(self):
        self.are_rules_done  = False
        self.are_groups_done = False

        self.attr_used = set()
        self.rel_used  = set()

        self.attr_unused = set()
        self.rel_unused  = set()

        self.cnt_rec   = Counter({ 'get_attr': 0, 'get_rel': 0, 'has_attr': 0, 'has_rel': 0 })  # recognized
        self.cnt_unrec = Counter({ 'get_attr': 0, 'get_rel': 0, 'has_attr': 0, 'has_rel': 0 })  # unrecognized


# ----------------------------------------------------------------------------------------------------------------------
class SimulationAdder(object):
    def __init__(self, sim):
        self.sim = sim

    def done(self):
        return self.sim

    def group(self, group):
        self.sim.add_group(group)
        return self

    def groups(self, groups):
        self.sim.add_groups(groups)
        return self

    def probe(self, probe):
        self.sim.add_probe(probe)
        return self

    def probes(self, probes):
        self.sim.add_probes(probes)
        return self

    def rule(self, rule):
        self.sim.add_rule(rule)
        return self

    def rules(self, rules):
        self.sim.add_rules(rules)
        return self

    def site(self, site):
        self.sim.add_site(site)
        return self

    def sites(self, sites):
        self.sim.add_sites(sites)
        return self


# ----------------------------------------------------------------------------------------------------------------------
class SimulationDBI(object):
    def __init__(self, sim, fpath):
        self.sim = sim
        self.fpath = fpath

        FS.req_file(fpath, f'The database does not exist: {fpath}')

    def done(self):
        return self.sim

    def gen_groups(self, tbl, attr_db=[], rel_db=[], attr_fix={}, rel_fix={}, rel_at=None, limit=0, is_verbose=False):
        self.sim.gen_groups_from_db(self.fpath, tbl, attr_db, rel_db, attr_fix, rel_fix, rel_at, limit, is_verbose)
        return self


# ----------------------------------------------------------------------------------------------------------------------
class SimulationPlotter(object):
    def __init__(self, sim):
        self.sim = sim

    def done(self):
        return self.sim

    def group_size(self, do_log=False, fpath=None, title='Distribution of Group Size', nx=250):
        self.sim.plot_group_size(do_log, fpath, title, nx)
        return self


# ----------------------------------------------------------------------------------------------------------------------
class SimulationSetter(object):
    def __init__(self, sim):
        self.sim = sim

    def done(self):
        return self.sim

    def dur(self, dur):
        self.sim.set_dur(dur)
        return self

    def iter_cnt(self, n):
        self.sim.set_iter_cnt(n)
        return self

    def fn_group_setup(self, fn):
        self.sim.set_fn_group_setup(fn)
        return self

    def pragma(self, name, value):
        self.sim.set_pragma(name, value)
        return self

    def pragma_analyze(self, value):
        self.sim.set_pragma_analyze(value)
        return self

    def pragma_autocompact(self, value):
        self.sim.set_pragma_autocompact(value)
        return self

    def pragma_autoprune_groups(self, value):
        self.sim.set_pragma_autoprune_groups(value)
        return self

    def pragma_autostop(self, value):
        self.sim.set_pragma_autostop(value)
        return self

    def pragma_autostop_n(self, value):
        self.sim.set_pragma_autostop_n(value)
        return self

    def pragma_autostop_p(self, value):
        self.sim.set_pragma_autostop_p(value)
        return self

    def pragma_autostop_t(self, value):
        self.sim.set_pragma_autostop_t(value)
        return self

    def pragma_live_info(self, value):
        self.sim.set_pragma_live_info(value)
        return self

    def pragma_live_info_ts(self, value):
        self.sim.set_pragma_live_info_ts(value)
        return self

    def pragma_probe_capture_init(self, value):
        self.sim.set_pragma_probe_capture_init(value)
        return self

    def pragma_rule_analysis_for_db_gen(self, value):
        self.sim.set_pragma_rule_analysis_for_db_gen(value)
        return self

    def rand_seed(self, rand_seed):
        self.sim.set_rand_seed(rand_seed)
        return self


# ----------------------------------------------------------------------------------------------------------------------
class Simulation(object):
    '''
    A PRAM simulation.

    At this point, this simulation is a discrete-event simulation (DES).  DES models the operation of a system as a
    (discrete) sequence of events in time.  DES contrast with continuous simulation in which the system state is
    changed continuously over time on the basis of a set of differential equations defining the rates of change of
    state variables.
    '''

    def __init__(self, traj=None, rand_seed=None, do_keep_mass_flow_specs=False):
        self.set_rand_seed(rand_seed)

        self.traj = traj  # trajectory
        self.run_cnt = 0

        self.pop = GroupPopulation(self, do_keep_mass_flow_specs)
        self.rules = []
        self.probes = []

        self.timer = None  # value deduced in add_group() based on rule timers

        self.is_setup_done = False  # flag
            # ensures simulation setup is performed only once while enabling multiple incremental simulation runs of
            # arbitrary length thus promoting interactivity (a sine qua non for a user interface)

        self.running = DotMap(
            is_running = False,
            progress = 0.0,
            step = 1.0
        )

        self.fn = DotMap(
            group_setup = None  # called before the simulation is run for the very first time
        )

        self.analysis = DotMap(
            rule_static  = StaticRuleAnalyzer(),
            rule_dynamic = DynamicRuleAnalyzer(self)
        )

        self.pragma = DotMap(
            analyze = True,                  # flag: analyze the simulation and suggest improvements?
            autocompact = False,             # flag: remove empty groups after every iteration?
            autoprune_groups = False,        # flag: remove attributes and relations not referenced by rules?
            autostop = False,                # flag
            autostop_n = 0,                  #
            autostop_p = 0,                  #
            autostop_t = 10,                 #
            live_info = False,               #
            live_info_ts = False,            #
            probe_capture_init = True,       # flag: let probes capture the pre-run state of the simulation?
            rule_analysis_for_db_gen = True  # flag: should static rule analysis results help form DB groups
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.rand_seed or ""})'

    def _inf(self, msg):
        if not self.pragma.live_info:
            return

        if self.pragma.live_info_ts:
            print(f'[{datetime.datetime.now()}: info] {msg}')
        else:
            print(f'[info] {msg}')

    def add(self, lst=None):
        if lst:
            for i in lst:
                if isinstance(i, Group):
                    self.add_group(i)
                elif isinstance(i, Probe):
                    self.add_probe(i)
                elif isinstance(i, Rule):
                    self.add_rule(i)
                elif isinstance(i, Site):
                    self.add_site(i)
            return self
        else:
            return SimulationAdder(self)

    def add_group(self, group):
        # No rules present:
        if len(self.rules) == 0:
            raise SimulationConstructionError('A group is being added but no rules are present; rules need to be added before groups.')

        # No groups present:
        if len(self.pop.groups) == 0:  # run when the first group is being added (because that marks the end of adding rules)
            if not self.analysis.rule_static.are_rules_done:
                self.analyze_rules_static()

            # Sync simulation and rules timers:
            rule_t_unit_ms = min([r.T_UNIT_MS for r in self.rules])
            self.timer = Timer.by_ms(rule_t_unit_ms, iter=0)

        self.pop.add_group(group)
        return self

    def add_groups(self, groups):
        for g in groups:
            self.add_group(g)
        return self

    def add_probe(self, probe):
        self.probes.append(probe)
        probe.set_pop(self.pop)
        return self

    def add_probes(self, probes):
        for p in probes:
            self.add_probe(p)
        return self

    def add_rule(self, rule):
        if len(self.rules) == 0:
            self._inf('Constructing a PRAM')

        if len(self.pop.groups) > 0:
            raise SimulationConstructionError('A rule is being added but groups already exist; rules need be added before groups.')

        self.rules.append(rule)
        self.analysis.rule_static.analyze_rules(self.rules)  # keep the results of the static rule analysis current

        return self

    def add_rules(self, rules):
        for r in rules:
            self.add_rule(r)
        return self

    def add_site(self, site):
        self.pop.add_site(site)
        return self

    def add_sites(self, sites):
        self.pop.add_sites(sites)
        return self

    def analyze_rules_static(self):
        '''
        Analyze rule conditioning prior to running the simulation.  This is done by analyzing the syntax (i.e.,
        abstract syntax trees or ASTs) of rule objects to identify group attributes and relations these rules condition
        on.  This is a difficult problem and the current implementation leaves room for future improvement.  In fact,
        the current algorithm works only if the names of attributes and relations are specified in the code of rules as
        string literals.  For example, if an attribute name is stored in a variable or is a result of a method call, it
        will not be captured by this algorithm.

        As a consequence, it is not possible to perform error-free groups auto-pruning based on this analysis.
        '''

        self._inf('Running static rule analysis')

        self.analysis.rule_static.analyze_rules(self.rules)

        self._inf(f'    Relevant attributes found : {list(self.analysis.rule_static.attr_used)}')
        self._inf(f'    Relevant relations  found : {list(self.analysis.rule_static.rel_used)}')

        return self

    def analyze_rules_dynamic(self):
        self._inf('Running dynamic rule analysis')

        rd = self.analysis.rule_dynamic
        rd.analyze()

        if self.pragma.live_info:
            self._inf(f'    Accessed attributes    : {list(rd.attr_used)}')
            self._inf(f'    Accessed relations     : {list(rd.rel_used)}')
            self._inf(f'    Superfluous attributes : {list(rd.attr_unused)}')
            self._inf(f'    Superfluous relations  : {list(rd.rel_unused )}')
        else:
            if self.pragma.analyze and (len(rd.attr_unused) > 0 or len(rd.rel_unused) > 0):
                print('Based on the most recent simulation run, the following group attributes A and relations R are superfluous:')
                print(f'    A: {list(rd.attr_unused)}')
                print(f'    R: {list(rd.rel_unused )}')

        return self

    def analyze_rules_dynamic_old(self):
        '''
        Analyze rule conditioning after running the simulation.  This is done by processing group attributes and
        relations that the simulation has recorded as accessed by at least one rule.  The evidence of attributes and
        relations having been actually accessed is a strong one.  However, as tempting as it may be to use this
        information to prune groups, it's possible that further simulation iterations depend on other sets of
        attributes and relations.  As a consequence, it is not possible to perform error-free groups auto-pruning based
        on this analysis alone.
        '''

        self._inf('Running dynamic rule analysis')

        lr = self.analysis.rule_dynamic
        lr.clear()

        lr.attr_used = getattr(Group, 'attr_used').copy()  # attributes conditioned on by at least one rule
        lr.rel_used  = getattr(Group, 'rel_used').copy()   # relations

        lr.attr_groups = set()  # attributes defining groups
        lr.rel_groups  = set()  # relations
        for g in self.pop.groups.values():
            for ga in g.attr.keys(): lr.attr_groups.add(ga)
            for gr in g.rel.keys():  lr.rel_groups. add(gr)

        lr.attr_unused = lr.attr_groups - lr.attr_used  # attributes not conditioned on by even one rule
        lr.rel_unused  = lr.rel_groups  - lr.rel_used   # relations

        if self.pragma.live_info:
            self._inf(f'    Accessed attributes    : {list(self.analysis.rule_dynamic.attr_used)}')
            self._inf(f'    Accessed relations     : {list(self.analysis.rule_dynamic.rel_used)}')
            self._inf(f'    Superfluous attributes : {list(lr.attr_unused)}')
            self._inf(f'    Superfluous relations  : {list(lr.rel_unused )}')
        else:
            if self.pragma.analyze and (len(lr.attr_unused) > 0 or len(lr.rel_unused) > 0):
                print('Based on the most recent simulation run, the following group attributes A and relations R are superfluous:')
                print(f'    A: {list(lr.attr_unused)}')
                print(f'    R: {list(lr.rel_unused )}')

        return self

    def clear_probes(self):
        self.probes.clear()
        return self

    def clear_rules(self):
        self.rules.clear()
        return self

    def commit_group(self, group):
        self.add_group(group)
        return self

    def compact(self):
        self.pop.compact()
        return self

    def db(self, fpath):
        return SimulationDBI(self, fpath)

    def gen_groups_from_db(self, fpath_db, tbl, attr_db=[], rel_db=[], attr_fix={}, rel_fix={}, rel_at=None, limit=0, is_verbose=False):
        if not self.analysis.rule_static.are_rules_done:
            self.analyze_rules_static()  # by now we know all rules have been added

        self._inf(f"Generating groups from a database ({fpath_db}; table '{tbl}')")

        if self.pragma.rule_analysis_for_db_gen:
            attr_db.extend(self.analysis.rule_static.attr_used)
            # rel_db  = self.analysis.rule_static.rel_used  # TODO: Need to use entity.GroupDBRelSpec class

        fn_live_info = self._inf if self.pragma.live_info else None
        self.add_groups(Group.gen_from_db(fpath_db, tbl, attr_db, rel_db, attr_fix, rel_fix, rel_at, limit, fn_live_info))
        return self

    def gen_groups_from_db_old(self, fpath_db, tbl, attr={}, rel={}, attr_db=[], rel_db=[], rel_at=None, limit=0, fpath=None, is_verbose=False):
        if not self.analysis.rule_static.are_rules_done:
            self.analyze_rules_static()  # by now we know all rules have been added

        self._inf(f"Generating groups from a database ({fpath_db}; table '{tbl}')")

        if self.pragma.rule_analysis_for_db_gen:
            # self._inf('    Using relevant attributes and relations')

            attr_db.extend(self.analysis.rule_static.attr_used)
            # rel_db  = self.analysis.rule_static.rel_used  # TODO: Need to use entity.GroupDBRelSpec class

        # fn_gen = lambda: Group.gen_from_db(fpath_db, tbl, attr, rel, attr_db, rel_db, rel_at, limit)
        # fn_gen = lambda: Group.gen_from_db(self, fpath_db, tbl, attr, rel, attr_db, rel_db, rel_at, limit)
        # groups = FS.load_or_gen(fpath, fn_gen, 'groups', is_verbose)

        groups = Group.gen_from_db(self, fpath_db, tbl, attr, rel, attr_db, rel_db, rel_at, limit)
        self.add_groups(groups)
        return self

    @staticmethod
    def gen_sites_from_db(fpath_db, fn_gen=None, fpath=None, is_verbose=False, pragma_live_info=False, pragma_live_info_ts=False):
        if pragma_live_info:
            if pragma_live_info_ts:
                print(f'[{datetime.datetime.now()}: info] Generating sites from the database ({fpath_db})')
            else:
                print(f'[info] Generating sites from the database ({fpath_db})')

        return FS.load_or_gen(fpath, lambda: fn_gen(fpath_db), 'sites', is_verbose)

    def gen_sites_from_db_new(self, fpath_db, tbl, name_col, rel_name=Site.AT, attr=[], limit=0):
        self._inf(f'Generating sites from a database ({fpath_db})')

        self.add_sites(Site.gen_from_db(fpath_db, tbl, name_col, rel_name, attr, limit))

    def get_pragma(self, name):
        fn = {
            'analyze'                  : self.get_pragma_analyze,
            'autocompact'              : self.get_pragma_autocompact,
            'autoprune_groups'         : self.get_pragma_autoprune_groups,
            'autostop'                 : self.get_pragma_autostop,
            'autostop_n'               : self.get_pragma_autostop_n,
            'autostop_p'               : self.get_pragma_autostop_p,
            'autostop_t'               : self.get_pragma_autostop_t,
            'live_info'                : self.get_pragma_live_info,
            'live_info_ts'             : self.get_pragma_live_info_ts,
            'probe_capture_init'       : self.get_pragma_probe_capture_init,
            'rule_analysis_for_db_gen' : self.get_pragma_rule_analysis_for_db_gen
        }.get(name, None)

        if fn is None:
            raise TypeError(f"Pragma '{name}' does not exist.")

        return fn()

    def get_pragma_analyze(self):
        return self.pragma.analyze

    def get_pragma_autocompact(self):
        return self.pragma.autocompact

    def get_pragma_autoprune_groups(self):
        return self.pragma.autoprune_groups

    def get_pragma_autostop(self):
        return self.pragma.autostop

    def get_pragma_autostop_n(self):
        return self.pragma.autostop_n

    def get_pragma_autostop_p(self):
        return self.pragma.autostop_p

    def get_pragma_autostop_t(self):
        return self.pragma.autostop_t

    def get_pragma_live_info(self):
        return self.pragma.live_info

    def get_pragma_live_info_ts(self):
        return self.pragma.live_info_ts

    def get_pragma_probe_capture_init(self):
        return self.pragma.probe_capture_init

    def get_pragma_rule_analysis_for_db_gen(self):
        return self.pragma.rule_analysis_for_db_gen

    def get_state(self, do_camelize=True):
        return {
            'sim': {
                'runCnt': self.run_cnt,
                'timer': {
                    'iter': (self.timer.i if self.timer else 0)
                },
                'run': {
                    'isRunning': self.running.is_running,
                    'progress': self.running.progress
                },
                'pragma': {
                    'analyze'                  : self.get_pragma_analyze(),
                    'autocompact'              : self.get_pragma_autocompact(),
                    'autoprune_groups'         : self.get_pragma_autoprune_groups(),
                    'autostop'                 : self.get_pragma_autostop(),
                    'autostop_n'               : self.get_pragma_autostop_n(),
                    'autostop_p'               : self.get_pragma_autostop_p(),
                    'autostop_t'               : self.get_pragma_autostop_t(),
                    'live_info'                : self.get_pragma_live_info(),
                    'live_info_ts'             : self.get_pragma_live_info_ts(),
                    'probe_capture_init'       : self.get_pragma_probe_capture_init(),
                    'rule_analysis_for_db_gen' : self.get_pragma_rule_analysis_for_db_gen()
                }
            },
            'pop': {
                'agentMass' : self.pop.get_mass(),
                'groupCnt'  : self.pop.get_group_cnt(),
                'siteCnt'   : self.pop.get_site_cnt()
            },
            'probes': {
                'ls': [{ 'name': p.name } for p in self.probes]
            },
            'rules': {
                'ls': [{ 'cls': r.__class__.__name__, 'name': r.__class__.NAME } for r in self.rules],
                'analysis': {
                    'static': {
                        'attr': {
                            'used'   : list(self.analysis.rule_static.attr_used),
                            'unused' : list(self.analysis.rule_static.attr_unused)
                        },
                        'rel': {
                            'used'    : list(self.analysis.rule_static.rel_used),
                            'unused'  : list(self.analysis.rule_static.rel_unused)
                        }
                    },
                    'dynamic': {
                        'attrUsed' : list(self.analysis.rule_dynamic.attr_used),
                        'relUsed'  : list(self.analysis.rule_dynamic.rel_used),
                        'attrUnused' : list(self.analysis.rule_dynamic.attr_unused),
                        'relUnused'  : list(self.analysis.rule_dynamic.rel_unused )
                    }
                }
            }
        }

    @staticmethod
    def _load(fpath, fn):
        with fn(fpath, 'rb') as f:
            gc.disable()
            sim = pickle.load(f)
            gc.enable()
            return sim

    @staticmethod
    def load(fpath):
        return Simulation._unpickle(fpath, open)

    @staticmethod
    def load_bz2(fpath):
        return Simulation._unpickle(fpath, bz2.BZ2File)

    @staticmethod
    def load_gz(fpath):
        return Simulation._unpickle(fpath, gzip.GzipFile)

    def new_group(self, m=0.0, name=None):
        # return Group(name or self.pop.get_next_group_name(), n, callee=self)
        return Group(name, m, callee=self)

    def plot(self):
        return SimulationPlotter(self)

    def plot_group_size(self, do_log=False, fpath=None, title='Distribution of Group Size', nx=250):
        '''
        nx - Number of x-axis points
        '''

        # Data:
        data = [g.n for g in self.pop.groups.values()]
        density = gaussian_kde(data)
        x = np.linspace(min(data), max(data), nx)
        density.covariance_factor = lambda: .25
        density._compute_covariance()

        # Figure:
        fig = plt.figure(figsize=(12,2))
        if title:
            plt.title(title)
        plt.plot(x, density(x), lw=1, linestyle='-', c='#666666', mfc='none', antialiased=True)  # marker='o', markersize=5
        # plt.legend(['Susceptible', 'Exposed', 'Recovered'], loc='upper right')
        plt.ylabel('Density')
        if do_log:
            plt.xlabel('Group size (log)')
            plt.xscale('log')
        else:
            plt.xlabel('Group size')
        plt.grid(alpha=0.25, antialiased=True)

        # Return:
        if fpath:
            fig.savefig(fpath, dpi=300, bbox_inches='tight')
            return self
        else:
            return fig

    def plot_site_size(self, do_log=False, fpath=None, title='Distribution of Site Size', nx=250):
        '''
        nx - Number of x-axis points
        '''

        # Data:
        data = [g.n for g in self.pop.groups.values()]
        density = gaussian_kde(data)
        x = np.linspace(min(data), max(data), nx)
        density.covariance_factor = lambda: .25
        density._compute_covariance()

        # Figure:
        fig = plt.figure(figsize=(12,2))
        if title:
            plt.title(title)
        plt.plot(x, density(x), lw=1, linestyle='-', c='#666666', mfc='none', antialiased=True)  # marker='o', markersize=5
        plt.ylabel('Density')
        if do_log:
            plt.xlabel('Group size (log)')
            plt.xscale('log')
        else:
            plt.xlabel('Group size')
        plt.grid(alpha=0.25, antialiased=True)

        # Return:
        if fpath:
            fig.savefig(fpath, dpi=300, bbox_inches='tight')
            return self
        else:
            return fig

    def rem_probe(self, probe):
        self.probes.discard(probe)
        return self

    def rem_rule(self, rule):
        self.rules.discard(rule)
        return self

    def reset_pop(self):
        self.run_cnt = 0
        self.is_setup_done = False
        self.pop = GroupPopulation()
        gc.collect()
        return self

    def reset_probes(self):
        self.probes = []
        return self

    def reset_rules(self):
        self.rules = []
        self.analysis.rule_static.reset()
        return self

    def run(self, iter_or_dur=1, do_disp_t=False):
        '''
        One by-product of running the simulation is that the simulation stores all group attributes and relations that
        are conditioned on by at least one rule.  After the run is over, a set of unused attributes and relations is
        produced, unless silenced.  That output may be useful for making future simulations more efficient by allowing
        the user to remove the unused bits which result in unnecessary group space partitioning.
        '''

        # No rules or groups:
        if len(self.rules) == 0:
            print('No rules are present\nExiting')
            return self

        if len(self.pop.groups) == 0:
            print('No groups are present\nExiting')
            return self

        self.pop.freeze()  # need to freeze the population to prevent splitting to count as new group counts

        # Decode iterations/duration:
        self._inf('Setting simulation duration')

        self.running.is_running = True
        self.running.progress = 0.0
        if isinstance(iter_or_dur, int):
            self.timer.add_iter(iter_or_dur)
            self.running.step = 1.0 / float(iter_or_dur)
        elif isinstance(iter_or_dur, str):
            self.timer.add_dur(Time.dur2ms(iter_or_dur))
            # self.running.step = ...  # TODO
        else:
            raise ValueError(f'Number of iterations or duration must be an integer or a string: {iter_or_dur}')

        # Rule conditioning 01 -- Init:
        setattr(Group, 'attr_used', set())
        setattr(Group, 'rel_used',  set())

        # Sync simulation and rule timers:
        self._inf('Syncing rule timers')

        for r in self.rules:
            r.set_t_unit(self.timer.ms)

        # Rule setup and simulation compacting:
        if not self.is_setup_done:
            if self.fn.group_setup:
                self._inf('Running group setup')
                self.pop.apply_rules(self.fn.group_setup, 0, self.timer, is_sim_setup=True)

            self._inf('Running rule setup')
            self.pop.apply_rules(self.rules, 0, self.timer, is_rule_setup=True)
            self.is_setup_done = True

        if self.pragma.autocompact:
            self._inf('Compacting the model')
            self.compact()

        # Force probes to capture the initial state:
        if self.pragma.probe_capture_init and self.run_cnt == 0:
            self._inf('Capturing the initial state')

            for p in self.probes:
                p.run(None, None)

        # Run the simulation:
        self._inf('Initial population')
        self._inf(f'    Mass   : {"{:,}".format(int(self.pop.get_mass()))}')
        self._inf(f'    Groups : {"{:,}".format(self.pop.get_group_cnt())}')
        self._inf(f'    Sites  : {"{:,}".format(self.pop.get_site_cnt())}')
        self._inf('Running the PRAM')

        self.run_cnt += 1
        self.autostop_i = 0  # number of consecutive iterations the 'autostop' condition has been met for

        self.timer.start()
        for i in range(self.timer.get_i_left()):
            if self.pragma.live_info:
                self._inf(f'Iteration {self.timer.i + 1} of {self.timer.i_max}')
                self._inf(f'    Group count: {self.pop.get_group_cnt()}')
            elif do_disp_t:
                print(f't:{self.timer.get_t()}')

            # Apply rules:
            self.pop.apply_rules(self.rules, self.timer.get_i(), self.timer.get_t())
            m_flow = self.pop.last_iter.mass_flow_tot
            m_pop = float(self.pop.get_mass())
            if m_pop > 0:
                p_flow = float(m_flow) / m_pop
            else:
                p_flow = None

            # Run probes:
            for p in self.probes:
                p.run(self.timer.get_i(), self.timer.get_t())

            # Advance timer:
            self.timer.step()
            self.running.progress += self.running.step

            # Autostop:
            if self.pragma.autostop and p_flow is not None:
                if m_flow < self.pragma.autostop_n or p_flow < self.pragma.autostop_p:
                    self.autostop_i += 1
                else:
                    self.autostop_i = 0

                if self.autostop_i >= self.pragma.autostop_t:
                    if self.pragma.live_info:
                        self._inf('Autostop condition has been met; population mass transfered during the most recent iteration')
                        self._inf(f'    {m_flow} of {self.pop.get_mass()} = {p_flow * 100}%')
                        self.timer.stop()
                        break
                    else:
                        print('')
                        print('Autostop condition has been met; population mass transfered during the most recent iteration:')
                        print(f'    {m_flow} of {self.pop.get_mass()} = {p_flow * 100}%')
                        self.timer.stop()
                        break

            # Autocompact:
            if self.pragma.autocompact:
                self._inf(f'    Compacting the model')
                self.compact()

        self.timer.stop()

        self._inf(f'Final population info')
        self._inf(f'    Groups: {"{:,}".format(self.pop.get_group_cnt())}')

        # Rule conditioning 02 -- Analyze and cleanup:
        self.analysis.rule_static.analyze_groups(self.pop.groups.values())
        self.analyze_rules_dynamic()

        setattr(Group, 'attr_used', None)
        setattr(Group, 'rel_used',  None)
            # we want this None instead of just calling clear() to prevent dynamic rule analysis picking up on
            # calls to has_attr(), has_rel(), and others that happen via outside rules
        # getattr(Group, 'attr_used').clear()
        # getattr(Group, 'rel_used' ).clear()

        # Rule cleanup and simulation compacting:
        self._inf('Running rule cleanup')

        self.pop.apply_rules(self.rules, 0, self.timer, is_rule_cleanup=True)
        if self.pragma.autocompact:
            self._inf('Compacting the model')
            self.compact()

        self._inf('Finishing simulation')
        self.running.is_running = False
        self.running.progress = 1.0
        self.running.step = 1.0

        # Flush any buffered probe data:
        for p in self.probes:
            if p.persistance is not None:
                p.persistance.flush()

        return self

    def _save(self, fpath, fn):
        with fn(fpath, 'wb') as f:
            pickle.dump(self, f)

    def save(self, fpath):
        self._pickle(fpath, open)
        return self

    def save_bz2(self, fpath):
        self._pickle(fpath, bz2.BZ2File)
        return self

    def save_gz(self, fpath):
        self._pickle(fpath, gzip.GzipFile)
        return self

    def set(self):
        return SimulationSetter(self)

    def set_fn_group_setup(self, fn):
        self.fn.group_setup = fn
        return self

    def set_pragma(self, name, value):
        fn = {
            'analyze'                  : self.set_pragma_analyze,
            'autocompact'              : self.set_pragma_autocompact,
            'autoprune_groups'         : self.set_pragma_autoprune_groups,
            'autostop'                 : self.set_pragma_autostop,
            'autostop_n'               : self.set_pragma_autostop_n,
            'autostop_p'               : self.set_pragma_autostop_p,
            'autostop_t'               : self.set_pragma_autostop_t,
            'live_info'                : self.set_pragma_live_info,
            'live_info_ts'             : self.set_pragma_live_info_ts,
            'probe_capture_init'       : self.set_pragma_probe_capture_init,
            'rule_analysis_for_db_gen' : self.set_pragma_rule_analysis_for_db_gen
        }.get(name, None)

        if fn is None:
            raise TypeError(f"Pragma '{name}' does not exist.")

        fn(value)
        return self

    def set_pragma_analyze(self, value):
        self.pragma.analyze = value
        return self

    def set_pragma_autocompact(self, value):
        self.pragma.autocompact = value
        return self

    def set_pragma_autoprune_groups(self, value):
        self.pragma.autoprune_groups = value
        return self

    def set_pragma_autostop(self, value):
        self.pragma.autostop = value
        return self

    def set_pragma_autostop_n(self, value):
        self.pragma.autostop_n = value
        return self

    def set_pragma_autostop_p(self, value):
        self.pragma.autostop_p = value
        return self

    def set_pragma_autostop_t(self, value):
        self.pragma.autostop_t = value
        return self

    def set_pragma_live_info(self, value):
        self.pragma.live_info = value
        return self

    def set_pragma_live_info_ts(self, value):
        self.pragma.live_info_ts = value
        return self

    def set_pragma_probe_capture_init(self, value):
        self.pragma.probe_capture_init = value
        return self

    def set_pragma_rule_analysis_for_db_gen(self, value):
        self.pragma.rule_analysis_for_db_gen = value
        return self

    def set_iter_cnt(self, iter_cnt):
        self.iter_cnt = iter_cnt
        return self

    def set_dur(self, dur):
        self.dur = dur
        if self.timer:
            self.timer.set_dur(dur)
        return self

    def set_rand_seed(self, rand_seed):
        self.rand_seed = rand_seed
        if self.rand_seed is not None:
            random.seed(self.rand_seed)
            np.random.seed(self.rand_seed)
        return self

    def show_rule_analysis(self):
        self.show_static_rule_analysis()
        self.show_dynamic_rule_analysis()

        return self

    def show_rule_analysis_dynamic(self):
        rd = self.analysis.rule_dynamic

        print( 'Most recent simulation run')
        print( '    Used')
        print(f'        Attributes : {list(rd.attr_used)}')
        print(f'        Relations  : {list(rd.rel_used)}')
        print( '    Groups')
        print(f'        Attributes : {list(rd.attr_groups)}')
        print(f'        Relations  : {list(rd.rel_groups)}')
        print( '    Superfluous')
        print(f'        Attributes : {list(rd.attr_unused)}')
        print(f'        Relations  : {list(rd.rel_unused)}')

        return self

    def show_rule_analysis_static(self):
        ra = self.analysis.rule_static

        print( 'Rule analyzer')
        print( '    Used')
        print(f'        Attributes : {list(ra.attr_used)}')
        print(f'        Relations  : {list(ra.rel_used)}')
        print( '    Superfluous')
        print(f'        Attributes : {list(ra.attr_unused)}')
        print(f'        Relations  : {list(ra.rel_unused)}')
        # print( '    Counts')
        # print(f'        Recognized   : get_attr:{ra.cnt_rec["get_attr"]} get_rel:{ra.cnt_rec["get_rel"]} has_attr:{ra.cnt_rec["has_attr"]} has_rel:{ra.cnt_rec["has_rel"]}')
        # print(f'        Unrecognized : get_attr:{ra.cnt_unrec["get_attr"]} get_rel:{ra.cnt_unrec["get_rel"]} has_attr:{ra.cnt_unrec["has_attr"]} has_rel:{ra.cnt_unrec["has_rel"]}')

        return self

    def summary(self, do_header=True, n_groups=8, n_sites=8, n_rules=8, n_probes=8, end_line_cnt=(0,0)):
        '''
        Prints the simulation summary.  The summary can be printed at any stage of a simulation (i.e., including at
        the very beginning and end) and parts of the summary can be shown and hidden and have their length specified.
        '''

        print('\n' * end_line_cnt[0], end='')

        if do_header:
            print( 'Simulation')
            print(f'    Random seed: {self.rand_seed}')
            print( '    Timing')
            print(f'        Timer: {self.timer}')
            print( '    Population')
            print(f'        Mass        : {"{:,.2f}".format(round(self.pop.get_mass(), 1))}')
            print(f'        Groups      : {"{:,}".format(self.pop.get_group_cnt())}')
            print(f'        Groups (ne) : {"{:,}".format(self.pop.get_group_cnt(True))}')
            print(f'        Sites       : {"{:,}".format(self.pop.get_site_cnt())}')
            print(f'        Rules       : {"{:,}".format(len(self.rules))}')
            print(f'        Probes      : {"{:,}".format(len(self.probes))}')

            if self.pragma.analyze:
                print( '    Static rule analysis')
                print( '        Used')
                print(f'            Attributes : {list(self.analysis.rule_static.attr_used)}')
                print(f'            Relations  : {list(self.analysis.rule_static.rel_used)}')
                print( '        Superfluous')
                print(f'            Attributes : {list(self.analysis.rule_static.attr_unused)}')
                print(f'            Relations  : {list(self.analysis.rule_static.rel_unused)}')
                print( '    Dynamic rule analysis')
                print( '        Used')
                print(f'            Attributes : {list(self.analysis.rule_dynamic.attr_used)}')
                print(f'            Relations  : {list(self.analysis.rule_dynamic.rel_used)}')
                # print('        Dynamic - Groups')
                # print(f'            Attributes : {list(self.analysis.rule_dynamic.attr_groups)}')
                # print(f'            Relations  : {list(self.analysis.rule_dynamic.rel_groups)}')
                print( '        Superfluous')
                print(f'            Attributes : {list(self.analysis.rule_dynamic.attr_unused)}')
                print(f'            Relations  : {list(self.analysis.rule_dynamic.rel_unused)}')

        if n_groups > 0:
            if len(self.pop.groups) > 0: print(f'    Groups ({"{:,}".format(len(self.pop.groups))})\n' + '\n'.join(['        {}'.format(g) for g in list(self.pop.groups.values())[:n_groups]]))
            if len(self.pop.groups) > n_groups: print('        ...')

        if n_sites > 0:
            if len(self.pop.sites)  > 0: print(f'    Sites ({"{:,}".format(len(self.pop.sites))})\n'   + '\n'.join(['        {}'.format(s) for s in list(self.pop.sites.values())[:n_sites]]))
            if len(self.pop.sites) > n_sites: print('        ...')

        if n_rules > 0:
            if len(self.rules)      > 0: print(f'    Rules ({"{:,}".format(len(self.rules))})\n'       + '\n'.join(['        {}'.format(r) for r in self.rules[:n_rules]]))
            if len(self.rules) > n_rules: print('        ...')

        if n_probes > 0:
            if len(self.probes)     > 0: print(f'    Probes ({"{:,}".format(len(self.probes))})\n'     + '\n'.join(['        {}'.format(p) for p in self.probes[:n_probes]]))
            if len(self.probes) > n_probes: print('        ...')

        print('\n' * end_line_cnt[1], end='')

        return self
