from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'w'

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
    'ocean_explicit_accel_b',
    'compute_tmask_limit',
    'eta_and_pbot_diagnose',
    'ocean_barotropic_forcing',
    'flux_adjust',
    #'rho_dzt_tendency',
]

#main_subroutines = [
#    'tracer',
#    'accel_a',
#    'vert_mix',
#    'submeso',
#    'barotropic',
#    'density',
#    'accel_imp',
#    'ucell_update',
#    'eta_smooth',
#    'sw',
#    'velocity',
#    'advect',
#    'tcell_update',
#    'density_diag',
#    'diag',
#    'sbc',
#    'accel_b',
#    'tmask_lim',
#    'eta_pbot_diag',
#    'bt_forcing',
#    'flux_adjust',
#    'rho_dzt_t',
#]

# Open MPI runtimes
with open('sis01_timings.yaml', 'r') as timings_file:
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
print(runtimes.keys())

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
        for subrt in runtimes.keys():
            mean_rt = run['runtimes'][subrt]
            try:
                subtimes[pe][subrt].append(mean_rt)
            except KeyError:
                subtimes[pe][subrt] = [mean_rt]

#----

fig, ax = plt.subplots(1, 1, figsize=(6., 6.))

peset = np.array(sorted(set(maintimes.keys())))
pe_widths = 500 * peset / peset[0]

ax.set_xscale('log')
ax.set_xlim(np.min(peset) * 0.9, np.max(peset) * 2.)
ax.set_xticks(peset + pe_widths / 2.)
ax.set_xticklabels(peset)
ax.set_xlabel('# of CPUs')
ax.set_ylim(0., 1.)
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

ax.legend(handles, main_subroutines, loc=(-0.7, 0.05), fontsize=10)
#ax.legend(main_subroutines, loc=(-0.6, 0.), fontsize=12)

plt.savefig('subscale01.svg', facecolor='none', bbox_inches='tight')
plt.close()
