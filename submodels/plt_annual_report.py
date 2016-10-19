from collections import defaultdict
import itertools as it
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('png', 'eps')
ctxt = 'k'

tname = 'loop'

# Open MPI runtimes
with open('new_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = {
        'ocn': [],
        'ice': [],
        'cpl': []
}

for expt in timings:
    for tname, rt in runtimes.items():
        for run in timings[expt]:
            npes = timings[expt][run]['npes']
            time = timings[expt][run]['runtimes'][tname]
            rt.append((npes, time))


peset = sorted(set([pt[0] for rt in runtimes for pt in runtimes[rt]]))

#fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
fig, ax_rt = plt.subplots(1, 1, figsize=(6, 6))

# Use one of the runtimes for configuration
rt_cfg = runtimes['ocn']


#for ax in (ax_rt,ax_eff):
for ax in (ax_rt,):
    ax.set_xscale('log')
    ax.set_xlim(100, 18000)
    #ax.set_ylim(1e0, 1e4)
    ax.set_xticks(peset)
    ax.set_xticklabels(peset, rotation=30)
    ax.set_xlabel('Number of CPU cores')

    ax.minorticks_off()

    # Set text color to white
    ax.xaxis.label.set_color(ctxt)
    ax.yaxis.label.set_color(ctxt)
    ax.title.set_color(ctxt)
    for label in it.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color(ctxt)

#fig.suptitle('Main loop', fontsize=16, color=ctxt)

ax_rt.set_yscale('log')
ax_rt.set_ylabel('Runtime (s)')
ax_rt.set_title('10-day model runtime')

#ax_eff.set_ylim(0., 1.1)
#ax_eff.set_title('10-day efficiency')

mk = {}
#mk['ocn'] = ('o', 'b')
#mk['ice'] = ('^', 'g')
#mk['cpl'] = ('v', 'r')
mk['ocn'] = ('o', 'orange')
mk['ice'] = ('^', 'purple')
mk['cpl'] = ('v', 'green')
handle = {}

# Plots
#ax_eff.axhline(1.0, color='k', linestyle='--')
#ax_eff.axhline(0.8, color='k', linestyle=':')

for tag in ('ocn', 'ice', 'cpl'):
    rt = runtimes[tag]

    # Plot theoretical speedup
    p_ref = 240
    pes = np.array(sorted(list(set(pt[0] for pt in rt))))

    # Theoretical scaling line
    t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
    t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
    t_opt = t_ref * p_ref / pes

    ax_rt.plot(pes, t_opt, '--', color=mk[tag][1])

    for pt in rt:
        (handle[tag],) = ax_rt.plot(pt[0], pt[1], mk[tag][0],
                                    markeredgewidth=1, markersize=8,
                                    color=mk[tag][1])

    pe_ref = 240
    t_min = np.min([pt[1] for pt in rt if pt[0] == pe_ref])

    #for pt in rt:
    #    ax_eff.plot(pt[0], t_min * pe_ref / (pt[0] * pt[1]), mk[tag][0],
    #                markeredgewidth=1, markersize=8, color=mk[tag][1])

ax_rt.legend([handle['ocn'], handle['ice'], handle['cpl']],
             ['Ocean', 'Sea Ice', 'Coupling'])

for fmt in formats:
    plt.savefig('submodels.{}'.format(fmt),
                facecolor='none', bbox_inches='tight')
