from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg', 'pdf', 'png')
ctxt = 'k'

# Open MPI runtimes
with open('barrier_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = defaultdict(list)

for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        for key in timings[expt][run]['runtimes']:
            rt = timings[expt][run]['runtimes'][key]
            runtimes[key].append((npes, rt))

            #min_rt = timings[expt][run]['runtimes'][key]['min']
            #mean_rt = timings[expt][run]['runtimes'][key]['mean']
            #max_rt = timings[expt][run]['runtimes'][key]['max']
            #std_rt = timings[expt][run]['runtimes'][key]['std']
            #runtimes[key].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Pie chart
main_routine = 'ocn'

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
        #'mpp_update_domain2d_r8_3d',
        'ocean_explicit_accel_b',
        'compute_tmask_limit',
        'eta_and_pbot_diagnose',
        'ocean_barotropic_forcing',
        #'flux_adjust',
        #'mpp_update_domain2d_r8_3dv',
        #'rho_dzt_tendency',
        #'compute_visc_form_drag',
        #'rivermix',
        #'sum_ocean_sfc',
        #'ocean_mass_forcing',
        #'eta_and_pbot_update',
        #'update_ocean_density_salinity',
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
        maintimes[pe].append(run['runtimes'][main_routine])
        for subrt in main_subroutines:
            mean_rt = run['runtimes'][subrt]
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

for fmt in formats:
    plt.savefig('pie025b.{}'.format(fmt), facecolor='none', bbox_inches='tight')

plt.close()
