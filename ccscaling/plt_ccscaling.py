from collections import defaultdict
import itertools as it
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('pdf', 'svg')
ctxt = 'w'

tname = 'loop'

rt_files = {'Serial': 'ompi_timings.yaml',
            'Concurrent': 'cc_timings.yaml'}

runtimes = {}

# Open MPI runtimes
for tag, fname in rt_files.items():
    with open(fname, 'r') as timings_file:
        timings = yaml.load(timings_file)

    runtimes[tag] = []
    for expt in timings:
        for run in timings[expt]:
            npes = timings[expt][run]['npes']
            time = timings[expt][run]['runtimes'][tname]
            runtimes[tag].append((npes, time))

fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
#fig.suptitle('Main loop scaling', fontsize=16, color='w')

#peset = sorted(set([pt[0] for rt in runtimes for pt in runtimes[rt]]))
peset = sorted(set([pt[0] for pt in runtimes['Concurrent']]))

for ax in (ax_rt, ax_eff):
    ax.set_xscale('log')
    ax.set_xlim(100, 10000)
    ax.set_xticks(peset)
    ax.set_xticklabels(peset, rotation=30)
    ax.set_xlabel('# of PEs')

    ax.minorticks_off()

    # Set text color to white
    ax.xaxis.label.set_color('w')
    ax.yaxis.label.set_color('w')
    ax.title.set_color('w')
    for label in it.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color('w')

ax_rt.set_yscale('log')
ax_rt.set_ylabel('Runtime (s)')
ax_rt.set_title('10-day runtime')

ax_eff.set_ylim(0., 1.1)
ax_eff.set_title('10-day efficiency')

markup = {}
markup['Serial'] = ('o', 'b', 240)
markup['Concurrent'] = ('d', 'r', 280)

handles = {}

for tag in runtimes:

    rt = runtimes[tag]
    mk = markup[tag]

    # Plot theoretical speedup
    p_ref = mk[2]
    pes = np.array(sorted(list(set(pt[0] for pt in rt))))

    t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
    t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
    t_opt = t_ref * p_ref / pes

    if tag == 'Concurrent':
        ax_rt.plot(pes, t_opt, '-', color='k', linestyle='--')

    # Plot Open MPI speedup
    for pt in rt:
        handles[tag], = ax_rt.plot(pt[0], pt[1], mk[0],
                                  markeredgewidth=1, markersize=8, color=mk[1])

    ax_eff.axhline(1., color='k', linestyle='--')
    ax_eff.axhline(0.8, color='k', linestyle=':')

    for pt in rt:
        ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], mk[0],
                    markeredgewidth=1, markersize=8, color=mk[1])

ax_rt.legend([handles['Serial'], handles['Concurrent']],
            ['Serial', 'Concurrent'])

for fmt in formats:
    plt.savefig('ccscaling_{}.{}'.format(tname, fmt),
                facecolor='none', bbox_inches='tight')
