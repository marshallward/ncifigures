from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
dark_bg = False

expt_timings = {
    'serial':   'serial_timings.yaml',
    'new':      'new_timings.yaml'
}

runtimes = {}
for runtype, timings_filename in expt_timings.items():

    with open(timings_filename, 'r') as timings_file:
        timings = yaml.load(timings_file)

    runtimes[runtype] = defaultdict(list)

    for expt in timings:
        for run in timings[expt]:
            ncpus = timings[expt][run]['ncpus']
            for key in timings[expt][run]['runtimes']:
                min_rt = timings[expt][run]['runtimes'][key]['min']
                mean_rt = timings[expt][run]['runtimes'][key]['mean']
                max_rt = timings[expt][run]['runtimes'][key]['max']
                std_rt = timings[expt][run]['runtimes'][key]['std']
                runtimes[runtype][key].append(
                    (ncpus, mean_rt, min_rt, max_rt, std_rt))


# Initialization IO (restart.ww3 reads)

serial_rts = runtimes['serial']['w3init_w3iors']
newinit_rts = runtimes['new']['w3init_w3iors']

# Filter out the "fast" cached IO results from `serial`
ncpus = sorted(list(set(rt[0] for rt in serial_rts)))

serial_maxrts = defaultdict(list)
serial_minrts = defaultdict(list)
newinit_maxrts = defaultdict(list)

for np in ncpus:
    np_rts = [rt[1] for rt in serial_rts if rt[0] == np]
    serial_maxrts[np] = max(np_rts)

    np_rts = [rt[1] for rt in serial_rts if rt[0] == np]
    serial_minrts[np] = min(np_rts)

    np_rts = [rt[1] for rt in newinit_rts if rt[0] == np]
    newinit_maxrts[np] = sum(np_rts) / len(np_rts)

# Initialization IO (restart.ww3 reads)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
fig.suptitle('Restart IO (initialization)', fontsize=16)

ax.set_xscale('log')
ax.set_xlim(0.75, 600)
ax.set_xlabel('# of PEs')
ax.set_xticks(ncpus)
ax.set_xticklabels(ncpus, rotation=0)
ax.minorticks_off()

ax.set_ylim(1e-1, 1e3)
ax.set_yscale('log')
ax.set_title('10-day runtime')

def_hdl, = ax.plot(list(serial_maxrts.keys()), list(serial_maxrts.values()),
        '^', markeredgewidth=1, markersize=8, color='g')
cch_hdl, = ax.plot(list(serial_minrts.keys()), list(serial_minrts.values()),
        'v', markeredgewidth=1, markersize=8, color='r')
mpi_hdl, = ax.plot(list(newinit_maxrts.keys()), list(newinit_maxrts.values()),
        'o', markeredgewidth=1, markersize=8, color='b')

ax.legend([def_hdl, cch_hdl, mpi_hdl],
          ['Default', 'Default (cached)', 'MPI-based'], loc='best')


plt.savefig('w3init_w3iors.pdf',
            facecolor='none', bbox_inches='tight')
