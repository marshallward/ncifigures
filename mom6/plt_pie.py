from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'w'

# Open MPI runtimes
with open('subrt_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = defaultdict(list)

for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        for key in timings[expt][run]['runtimes']:
            min_rt = timings[expt][run]['runtimes'][key]['min']
            mean_rt = timings[expt][run]['runtimes'][key]['mean']
            max_rt = timings[expt][run]['runtimes'][key]['max']
            std_rt = timings[expt][run]['runtimes'][key]['std']
            runtimes[key].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Pie chart
main_routine = 'update_ocean_model'

main_subroutines = [
        'update_ocean_tracer',
        'step_mom_dyn_split_rk2',
        'do_group_pass',
        'diabatic',
        'ale_main',
        'mixedlayer_restrat',
        'advect_tracer'
]

npes = set([timings[expt][run]['npes']
            for expt in timings for run in timings[expt]])

subtimes = {}
maintimes = {}
for pe in npes:
    subtimes[pe] = {}
    maintimes[pe] = []

for _, expt in timings.items():
    for rname, run in expt.items():
        pe = run['npes']
        maintimes[pe].append(run['runtimes'][main_routine]['mean'])
        for subrt in main_subroutines:
            mean_rt = run['runtimes'][subrt]['mean']
            try:
                subtimes[pe][subrt].append(mean_rt)
            except KeyError:
                subtimes[pe][subrt] = [mean_rt]

mean_times = {}

fig, ax = plt.subplots(1, 1, figsize=(7., 7.))
pe = 960

total = float(np.array([t for t in maintimes[pe]]).mean())

sizes = []
labels = []
for subrt in main_subroutines:
    sizes.append(float(np.array([t for t in subtimes[pe][subrt]]).mean()))
    labels.append(subrt)

# Unaccounted
sizes.append(total - np.array(sizes).sum())
labels.append('other')

nwedge = len(labels)
colormap = 'Set1'
cm = plt.get_cmap(colormap)
colors = cm([1. * i / nwedge for i in range(nwedge)])

ax.pie(sizes, colors=colors)

ax.set_title('Ocean subroutine runtimes at 960 CPUs', fontsize=16, color=ctxt)

ax.legend(labels, loc=(-0.5, 0.1), fontsize=10)

plt.savefig('pie025.svg', facecolor='none', bbox_inches='tight')
plt.close()
