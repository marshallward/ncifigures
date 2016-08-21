from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'k'

main_routine = 'ocean'

main_subroutines = [
        # Top-level
        #'ocn_dynamics',
        #'ocn_thermo',
        #'ocn_other',

        # Dynamics
        'rk2_coriolis',
        'rk2_continuity',
        'rk2_pressureforce',
        'rk2_vertvisc',
        'rk2_horvisc',
        #'rk2_momentum_update',
        'rk2_msg_pass',
        #'rk2_btcalc',
        'rk2_btstep',
        #'rk2_btforce',

        # "Other" (+ thermo?)
        'ocn_tracer',
        'ocn_diabatic',
        'ocn_continuity',
        'ocn_msg_pass',
        'ocn_thick_diff',
        'ocn_ml_restrat',
        'ocn_diag',
        'ocn_z_diag',
        'ocn_ale',

        # Init
        #'ocn_mom_init',
        #'ocn_msg_pass_init',
        #'rk2_msg_pass_init',
]

# Open MPI runtimes
with open('mom6_fms_block_timings.yaml', 'r') as timings_file:
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
pe_widths = 50 * peset / peset[0]

ax.set_xscale('log')
ax.set_xlim(np.min(peset) * 0.9, np.max(peset) * 2.)
ax.set_xticks(peset + pe_widths / 2.)
ax.set_xticklabels(peset)
ax.set_xlabel('# of CPUs')
#ax.set_ylim(0., 1.)
ax.set_ylabel('Relative runtime')
ax.set_title('Relative MOM6 component runtimes (blocked)')

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

plt.savefig('mom6_bars_fms_block.svg', facecolor='none', bbox_inches='tight')
plt.close()
