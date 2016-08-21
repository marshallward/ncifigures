from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('pdf', 'svg')

tname = 'loop'

# Intel Runtimes
with open('intel_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

intel_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes'][tname]
        intel_runtimes.append((npes, time))

# Open MPI runtimes
with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

ompi_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes'][tname]
        ompi_runtimes.append((npes, time))

peset = sorted(set([pt[0] for pt in ompi_runtimes]))

#plt.xticks(rotation=45)
fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12., 6.))

for ax in (ax_rt, ax_eff):
    ax.set_xscale('log')
    ax.set_xlim(100, 8000)
    ax.set_xticks(peset)
    ax.set_xticklabels(peset, rotation=30)
    ax.set_xlabel('# of PEs')

    # Set text color to white
    ax.xaxis.label.set_color('w')
    ax.yaxis.label.set_color('w')
    ax.title.set_color('w')
    for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color('w')

ax_rt.set_yscale('log')
ax_rt.set_ylabel('Runtime (s)')
ax_rt.set_title('10-day runtime ({})'.format(tname))

ax_eff.set_title('10-day efficiency')

# Plot theoretical speedup
p_ref = 240
pes = np.array(sorted(list(set(pt[0] for pt in intel_runtimes))))

t_ref = np.mean([pt[1] for pt in intel_runtimes if pt[0] == p_ref])
t_min = np.min([pt[1] for pt in intel_runtimes if pt[0] == p_ref])
t_min_ompi = np.min([pt[1] for pt in ompi_runtimes if pt[0] == p_ref])
t_opt = t_ref * p_ref / pes

ax_rt.plot(pes, t_opt, '--', color='k')

# Plot intel speedup
for pt in intel_runtimes:
    impi_handle, = ax_rt.plot(pt[0], pt[1], 'x', markersize=8, color='b')

# Plot open mpi speedup
for pt in ompi_runtimes:
    ompi_handle, = ax_rt.plot(pt[0], pt[1], 'x', markersize=8, color='r')

ax_rt.legend([impi_handle, ompi_handle], ['Intel MPI', 'OpenMPI'])

#---

ax_eff.axhline(1., color='k', linestyle='--')
ax_eff.axhline(0.8, color='k', linestyle=':')

for pt in intel_runtimes:
    ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'x', color='b')

for pt in ompi_runtimes:
    ax_eff.plot(pt[0], t_min_ompi * p_ref / pt[0] / pt[1], 'x', color='r')

for fmt in formats:
    plt.savefig('intel_ompi_{}.{}'.format(tname, fmt), facecolor='none',
                bbox_inches='tight')

# My reporting
intel_wt = defaultdict(list)

for pt in intel_runtimes:
    intel_wt[pt[0]].append(pt[1])

for pt in sorted(intel_wt):
    times = np.array(intel_wt[pt])
    print(pt, np.min(times), np.std(times))

ompi_wt = defaultdict(list)

for pt in ompi_runtimes:
    ompi_wt[pt[0]].append(pt[1])

print('open mpi')
for pt in sorted(ompi_wt):
    times = np.array(ompi_wt[pt])
    print(pt, np.min(times), np.std(times))
