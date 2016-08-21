from collections import defaultdict
import itertools as it
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'w'

tname = 'loop'
oname = 'model'

runtimes = {}

# Open MPI runtimes
with open('timings01.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

ompi_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes'][tname]
        ompi_runtimes.append((npes, time))

peset = sorted(set([pt[0] for pt in ompi_runtimes]))

fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle('Raijin 0.1° scaling', fontsize=16, color=ctxt)

for ax in (ax_rt, ax_eff):
    ax.set_xscale('log')
    ax.set_xlim(500, 2.5e4)
    ax.set_xticks(peset)
    ax.set_xticklabels(peset, rotation=30)
    ax.set_xlabel('# of CPUs')

    ax.minorticks_off()

    ax.xaxis.label.set_color(ctxt)
    ax.yaxis.label.set_color(ctxt)
    ax.title.set_color(ctxt)
    for label in it.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color(ctxt)

ax_rt.set_ylim(1e2, 2e4)
ax_rt.set_yscale('log')
ax_rt.set_ylabel('Runtime (s)')
ax_rt.set_title('10-day runtime')

ax_eff.set_ylim(0., 1.1)
ax_eff.set_title('10-day efficiency')

# Plot theoretical speedup
p_ref = 1250
pes = np.array(sorted(list(set(pt[0] for pt in ompi_runtimes))))

t_ref = np.mean([pt[1] for pt in ompi_runtimes if pt[0] == p_ref])
t_min = np.min([pt[1] for pt in ompi_runtimes if pt[0] == p_ref])
t_opt = t_ref * p_ref / pes

ax_rt.plot(pes, t_opt, '-', color='k', linestyle='--')

# Plot Open MPI speedup
for pt in ompi_runtimes:
    ompi_handle, = ax_rt.plot(pt[0], pt[1], 'd',
                              markeredgewidth=1, markersize=8, color='r')

#---
ax_eff.axhline(1., color='k', linestyle='--')
ax_eff.axhline(0.8, color='k', linestyle=':')

for pt in ompi_runtimes:
    ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'd',
                markeredgewidth=1, markersize=8, color='r')

for fmt in formats:
    plt.savefig('scaling01_{}.{}'.format(tname, fmt),
                facecolor='none', bbox_inches='tight')
