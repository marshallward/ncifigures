from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

#ext, ctxt = 'pdf', 'k'
ext, ctxt = 'svg', 'w'

# Open MPI runtimes
with open('timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = defaultdict(list)

for expt in timings:
    for run in timings[expt]:
        cice_npes = timings[expt][run]['ncpus']['cice5'][1]
        if cice_npes != 960:
            continue

        npes = timings[expt][run]['ncpus']['mom'][1]
        for key in timings[expt][run]['runtimes']:
            min_rt = timings[expt][run]['runtimes'][key]['min']
            mean_rt = timings[expt][run]['runtimes'][key]['mean']
            max_rt = timings[expt][run]['runtimes'][key]['max']
            std_rt = timings[expt][run]['runtimes'][key]['std']
            runtimes[key].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Pie chart
#main_routine = 'update_ocean_model'

main_subroutines = [
        'update_ocean_model',

        #'update_ocean_tracer',
        #'submeso_restrat',
        #'vert_mix_coeff',
        #'ocean_explicit_accel_a',
        #'ocean_diagnostics',
        #'update_ocean_density',
        #'update_ocean_barotropic',
        #'ocean_implicit_accel',
        #'get_ocean_sbc',
        #'eta_and_pbot_diagnose',
        #'sw_source',
        #'ocean_density_diag',
        #'update_ocean_velocity_bgrid',
        #'ocean_eta_smooth',
        #'update_ucell_thickness',
        #'ocean_advection_velocity',
        #'update_tcell_thickness',
        #'ocean_explicit_accel_b',
        #'compute_tmask_limit',

        'main_IP_external_coupler_sbc_before',
        'main_IP_external_coupler_sbc_after'
]

npes = set([timings[expt][run]['ncpus']['mom'][1]
            for expt in timings for run in timings[expt]])

subtimes = {}
maintimes = {}
for pe in npes:
    subtimes[pe] = {}
    maintimes[pe] = []

for _, expt in timings.items():
    for rname, run in expt.items():
        if run['ncpus']['cice5'][1] != 960:
            continue

        pe = run['ncpus']['mom'][1]

        main_rt = 0.
        for subrt in main_subroutines:
            mean_rt = run['runtimes'][subrt]['mean']
            try:
                subtimes[pe][subrt].append(mean_rt)
            except KeyError:
                subtimes[pe][subrt] = [mean_rt]

            main_rt += mean_rt
        maintimes[pe].append(main_rt)

mean_times = {}

#----

fig, ax = plt.subplots(1, 1, figsize=(6., 6.))

peset = np.array(sorted(set(maintimes.keys())))
pe_widths = 1000 * peset / peset[0]

ax.set_xscale('log')
ax.set_xlim(np.min(peset) * 0.66, np.max(peset) * 1.5)
ax.set_xticks(peset + pe_widths / 2.)
ax.set_xticklabels(peset)
ax.set_ylim(0., 1.05)
ax.set_xlabel('# of CPUs')
ax.set_ylabel('Relative runtime')
ax.set_title('Relative runtime of main loop subroutines')

ax.xaxis.label.set_color(ctxt)
ax.yaxis.label.set_color(ctxt)
ax.title.set_color(ctxt)
for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
    label.set_color(ctxt)

#----

main_rt = np.array([np.mean([t for t in maintimes[pe]]) for pe in peset])

btm_bar = np.zeros(main_rt.shape)
cm = plt.get_cmap('Set1')
n_subrt = len(main_subroutines)
colors = cm([1. * i / n_subrt for i in range(n_subrt)])

handles = []
for subrt, c_subrt in zip(main_subroutines, colors):

    subrt_times = np.array([np.mean([t for t in subtimes[pe][subrt]])
                            for pe in peset])

    h = plt.bar(peset, subrt_times / main_rt, pe_widths, bottom=btm_bar,
            color=c_subrt)
    btm_bar += subrt_times / main_rt

    handles.append(h)

ax.legend(handles[::-1], main_subroutines[::-1], loc=(-0.8, 0.3), fontsize=9)

plt.savefig('mom_bars.{}'.format(ext), facecolor='none', bbox_inches='tight')
plt.close()
