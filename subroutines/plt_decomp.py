from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)

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
        'ocean_explicit_accel_a',
        'vert_mix_coeff',
        'submeso_restrat',
        'update_ocean_barotropic',
        'update_ocean_density',
        'ocean_implicit_accel',
        'update_ucell_thickness',
        'ocean_eta_smooth',
        'sw_source',
        'update_ocean_velocity_bgrid',
        'ocean_advection_velocity',
        'update_tcell_thickness',
        'ocean_density_diag',
        'get_ocean_sbc',
        'ocean_diagnostics',
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

fig, axes = plt.subplots(2, 4, figsize=(16., 8.))

axlist = [a for axrow in axes for a in axrow]

for pe, ax in zip(sorted(npes), axlist[:7]):

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
    #colormap = 'Paired'
    colormap = 'gist_ncar'
    #colormap = 'nipy_spectral'
    #colormap = 'hsv'
    cm = plt.get_cmap(colormap)
    colors = cm([1. * i / nwedge for i in range(nwedge)])

    ax.pie(sizes, colors=colors)

    ax.set_title(pe)

axlist[-1].set_visible(False)
axlist[0].legend(labels, loc=(-1.5,-1.))

plt.savefig('pie.svg', facecolor='none', bbox_inches='tight')
plt.close()
