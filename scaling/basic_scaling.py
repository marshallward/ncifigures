from collections import defaultdict
import itertools as it
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('pdf', 'svg')

tname = 'loop'
oname = 'model'
dark_bg = False

runtimes = {}

# Open MPI runtimes
with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

ompi_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes'][tname]
        ompi_runtimes.append((npes, time))

# Open MPI runtimes
with open('raijin.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

orig_runtimes = []
for expt in timings:
    npes = timings[expt]['ncpus']
    time = timings[expt]['runtime'][oname] * 10. / 31.
    orig_runtimes.append((npes, time))

# Open MPI runtimes
with open('ht.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

ht_runtimes = []
for expt in timings:
    npes = timings[expt]['ncpus']
    time = timings[expt]['runtime'][oname] * 10. / 31.
    ht_runtimes.append((npes, time))

# Compatibility
npes = [p[0] for p in orig_runtimes]

orig_npes = np.array(sorted(npes))
orig_wt = np.array([p[1] for (i, p) in sorted(zip(npes, orig_runtimes))])
ht_wt = np.array([p[1] for (i, p) in sorted(zip(npes, ht_runtimes))])

peset = sorted(set([pt[0] for pt in ompi_runtimes]))

fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
#fig.suptitle('Main loop scaling', fontsize=16, color='w')

for ax in (ax_rt, ax_eff):
    ax.set_xscale('log')
    ax.set_xlim(100, 8000)
    ax.set_xticks(peset)
    ax.set_xticklabels(peset, rotation=30)
    ax.set_xlabel('# of PEs')

    ax.minorticks_off()

    # Set text color to white
    if dark_bg:
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

# Plot theoretical speedup
p_ref = 240
pes = np.array(sorted(list(set(pt[0] for pt in ompi_runtimes))))

t_ref = np.mean([pt[1] for pt in ompi_runtimes if pt[0] == p_ref])
t_min = np.min([pt[1] for pt in ompi_runtimes if pt[0] == p_ref])
t_opt = t_ref * p_ref / pes

ax_rt.plot(pes, t_opt, '-', color='k', linestyle='--')

## Plot original values
#orig_handle, = ax_rt.plot(orig_npes, orig_wt, linestyle=':', color='g')
#ht_handle, = ax_rt.plot(orig_npes, ht_wt, linestyle=':', color='b')

#t_min_orig = np.min([pt[1] for pt in orig_runtimes if pt[0] == p_ref])
#t_min_ht = np.min([pt[1] for pt in ht_runtimes if pt[0] == p_ref])

# Plot Open MPI speedup
for pt in ompi_runtimes:
    ompi_handle, = ax_rt.plot(pt[0], pt[1], 'd',
                              markeredgewidth=1, markersize=8, color='r')

#for pt in orig_runtimes:
#    orig_handle, = ax_rt.plot(pt[0], pt[1], '^',
#                              markeredgewidth=1, markersize=8, color='g')
#
#for pt in ht_runtimes:
#    ht_handle, = ax_rt.plot(pt[0], pt[1], 'v',
#                            markeredgewidth=1, markersize=8, color='b')
#
#ax_rt.legend([orig_handle, ht_handle, ompi_handle],
#             ['Original', 'Hyperthreaded', 'Latest'])

#---
#ax_eff.plot(orig_npes, t_min_orig * p_ref / (orig_wt * orig_npes),
#        linestyle=':', color='g')
#ax_eff.plot(orig_npes, t_min_ht * p_ref / (ht_wt * orig_npes),
#        linestyle=':', color='b')

ax_eff.axhline(1., color='k', linestyle='--')
ax_eff.axhline(0.8, color='k', linestyle=':')

for pt in ompi_runtimes:
    ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'd',
                markeredgewidth=1, markersize=8, color='r')

#for pt in orig_runtimes:
#    ax_eff.plot(pt[0], t_min_orig * p_ref / pt[0] / pt[1], '^',
#                markeredgewidth=1, markersize=8, color='g')
#
#for pt in ht_runtimes:
#    ax_eff.plot(pt[0], t_min_ht * p_ref / pt[0] / pt[1], 'v',
#                markeredgewidth=1, markersize=8, color='b')

for fmt in formats:
    plt.savefig('scaling_{}.{}'.format(tname, fmt),
                facecolor='none', bbox_inches='tight')
