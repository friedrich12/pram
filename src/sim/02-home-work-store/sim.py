'''
A simulation of agents going from home to work and then, sometimes, to a store and back home again.  Apart from
testing the mechanics of a simulation, this module mainly tests the GoToRule rule.
'''

from pram.data   import GroupSizeProbe, ProbeMsgMode
from pram.entity import GroupQry, Site
from pram.rule   import GoToRule, TimeInt, TimePoint
from pram.sim    import Simulation


# ----------------------------------------------------------------------------------------------------------------------
sites = {s:Site(s) for s in ['home', 'work-a', 'work-b', 'work-c', 'store-a', 'store-b']}

probe_grp_size_site = GroupSizeProbe.by_rel('site', Site.AT, sites.values(), msg_mode=ProbeMsgMode.DISP, memo='Mass distribution across sites')

(Simulation().
    add().
        rule(GoToRule(0.4, 'home',  'work',  TimeInt( 8,12), memo='Some agents leave home to go to work')).
        rule(GoToRule(0.4, 'work',  'home',  TimeInt(16,20), memo='Some agents return home from work')).
        rule(GoToRule(0.2, 'home',  'store', TimeInt(16,21), memo='Some agents go to a store after getting back home')).
        rule(GoToRule(0.3, 'store', 'home',  TimeInt(17,23), memo='Some shopping agents return home from a store')).
        rule(GoToRule(1.0, 'store', 'home',  TimePoint(24),  memo='All shopping agents return home after stores close')).
        rule(GoToRule(1.0, None,    'home',  TimePoint( 2),  memo='All still-working agents return home')).
        probe(probe_grp_size_site).
        done().
    new_group(m=1000).
        set_rel(Site.AT, sites['home']).
        set_rel('home',  sites['home']).
        set_rel('work',  sites['work-a']).
        set_rel('store', sites['store-a']).
        done().
    new_group(m=1000).
        set_rel(Site.AT, sites['home']).
        set_rel('home',  sites['home']).
        set_rel('work',  sites['work-b']).
        set_rel('store', sites['store-b']).
        done().
    new_group(m=100).
        set_rel(Site.AT, sites['home']).
        set_rel('home',  sites['home']).
        set_rel('work',  sites['work-c']).
        done().
    summary(True, end_line_cnt=(0,1)).
    run(24).
    summary(False, 20,0,0,0, end_line_cnt=(1,1)).
    set_pragma_analyze(False).
    run(4)
)
