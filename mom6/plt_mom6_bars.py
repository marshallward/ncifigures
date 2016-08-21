from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'k'

# Open MPI runtimes
with open('mom6_scorep_barrier_timings.yaml', 'r') as timings_file:
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
    #'step_mom_dyn_split_rk2',
    'step_mom_dyn_split_rk2__do_group_pass',
    'btstep',
    'step_mom_dyn_split_rk2__continuity',
    'pressureforce',
    #'step_mom_dyn_split_rk2__set_dtbt',
    'vertvisc_coef',
    'step_mom_dyn_split_rk2__horizontal_viscosity',
    'vertvisc_remnant',
    'coradcalc',
    'vertvisc',
    'step_mom_dyn_split_rk2__set_viscous_bbl',
    'step_mom_dyn_split_rk2__btcalc',
    'step_mom__do_group_pass',
    'diabatic',
    'step_mom__ale_main',
    'mixedlayer_restrat',
    'advect_tracer',
    'thickness_diffuse',
    'calc_slope_functions',
    'step_forward_meke',
    #'set_viscous_bbl',
    'tracer_hordiff',
    'calc_resoln_function',
    'step_mom__calculate_surface_state',
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
        main_rt = run['runtimes'][main_routine]['mean']

        maintimes[pe].append(main_rt)
        for subrt in main_subroutines:
            mean_rt = run['runtimes'][subrt]['mean']
            try:
                subtimes[pe][subrt].append(mean_rt)
            except KeyError:
                subtimes[pe][subrt] = [mean_rt]

mean_times = {}

#----

fig, ax = plt.subplots(1, 1, figsize=(6., 6.))

peset = np.array(sorted(set(maintimes.keys())))
pe_widths = 50 * peset / peset[0]

ax.set_xscale('log')
ax.set_xlim(np.min(peset) * 0.9, np.max(peset) * 2.)
ax.set_xticks(peset + pe_widths / 2.)
ax.set_xticklabels(peset)
ax.set_ylim(0., 1.)
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

ax.legend(handles, main_subroutines, loc=(-1.0, 0.0), fontsize=9)
#ax.legend(handles[::-1], main_subroutines[::-1], loc=(-0.6, 0.), fontsize=12)

plt.savefig('mom6_bars.svg', facecolor='none', bbox_inches='tight')
plt.close()
