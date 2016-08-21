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
with open('orca_scorep_timings.yaml', 'r') as timings_file:
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
main_routine = 'stp'

main_subroutines = [
    #'sbc',
    'dyn_spg',
    'tra_adv',
    'stp_ctl',
    'ldf_slp',
    'zdf_tke',
    'tra_dmp',
    'dyn_ldf',
    'tra_ldf',
    'stp__zps_hde',
    'zdf_tmx',
    'tra_qsr',
    'dyn_zdf',
    'tra_nxt',
    'tra_zdf',
    'ssh_wzv',
    'tra_bbl',
    'dyn_adv',
    'dia_wri',
    'tra_sbc',
    'eos_bn2',
    'dyn_nxt',
    'stp__eos_insitu_pot',
    'dyn_vor',
    #'eos_insitu',
    #'dyn_hpg',
    #'zdf_evd',
    #'zdf_mxl',
    #'zdf_bfr',
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

        # NEMO sbc correction
        if main_routine == 'stp':
            main_rt -= run['runtimes']['sbc']['mean']

        #maintimes[pe].append(run['runtimes'][main_routine]['mean'])
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
pe_widths = 12 * peset / peset[0]

ax.set_xscale('log')
ax.set_xlim(np.min(peset) * 0.9, np.max(peset) * 2.)
ax.set_xticks(peset + pe_widths / 2.)
ax.set_xticklabels(peset)
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

ax.legend(handles, main_subroutines, loc=(-0.5, 0.0), fontsize=9)
#ax.legend(handles[::-1], main_subroutines[::-1], loc=(-0.6, 0.), fontsize=12)

plt.savefig('nemo_bars.svg', facecolor='none', bbox_inches='tight')
plt.close()
