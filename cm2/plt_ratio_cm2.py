from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'k'
submodels = ('atm', 'ocn', 'ice')
default_ncpus = {
        'atm': 432,
        'ice': 192,
        'ocn': 960,
}

main_routine = {}
main_subroutines = {}
init_subroutines = {}

main_routine['atm'] = 'u_model_4a'
main_routine['ice'] = 'cice_run'
#main_routine['ocn'] = 'MAIN'

main_subroutines['atm'] = [
        'atm_step_4a',
        'oasis3_geto2a',
        'oasis3_puta2o',
        'dumpctl',
        'meanctl',
]

main_subroutines['ice'] = [
        'ice_step',
        'into_atm',
        'into_ocn',
        'from_ocn',
        #'save_restart_mice',
        #'t2ugrid_vector',
        'from_atm',
]

main_subroutines['ocn'] = [
        #'main_IP_ice_ocn_bnd_from_data',
        'main_IP_external_coupler_sbc_before',
        'update_ocean_model',
        'main_IP_external_coupler_sbc_after',
]

init_subroutines['atm'] = [
        'initial_4a',
]

with open('cm2.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

maintimes = {}
subtimes = {}

for regsub in submodels:
    maintimes[regsub] = {}
    subtimes[regsub] = {}

    for cpusub in submodels:
        maintimes[regsub][cpusub] = {}
        subtimes[regsub][cpusub] = {}

inittimes = {}
inittimes['atm'] = {}
for cpusub in submodels:
    inittimes['atm'][cpusub] = {}


for regsub in submodels:
    # Skip 'ocn' for now
    #if regsub == 'ocn':
    #    continue

    for cpusub in submodels:
        for expt in timings:
            # Skip non-default off-axis cpu layouts
            if any(default_ncpus[s] != timings[expt][s]['n']
                   for s in submodels if s is not cpusub):
                continue

            ncpus = timings[expt][cpusub]['n']

            # Process main subroutine

            if regsub in main_routine:
                main_reg = main_routine[regsub]
                rt = timings[expt][regsub]['runtimes'][main_reg]['mean']

                if not ncpus in maintimes[regsub][cpusub]:
                    maintimes[regsub][cpusub][ncpus] = []

                maintimes[regsub][cpusub][ncpus].append(rt)

            # Process subroutine data

            for reg in main_subroutines[regsub]:
                rt = timings[expt][regsub]['runtimes'][reg]['mean']

                if not ncpus in subtimes[regsub][cpusub]:
                    subtimes[regsub][cpusub][ncpus] = {}

                try:
                    subtimes[regsub][cpusub][ncpus][reg].append(rt)
                except KeyError:
                    subtimes[regsub][cpusub][ncpus][reg] = [rt]

            # Initialization subroutines

            if regsub in init_subroutines:
                for reg in init_subroutines[regsub]:
                    rt = timings[expt][regsub]['runtimes'][reg]['mean']

                    if not ncpus in inittimes[regsub][cpusub]:
                        inittimes[regsub][cpusub][ncpus] = {}

                    try:
                        inittimes[regsub][cpusub][ncpus][reg].append(rt)
                    except KeyError:
                        inittimes[regsub][cpusub][ncpus][reg] = [rt]

# Create figure directories
try:
    os.mkdir('barfigs')
except FileExistsError:
    pass


# Plot figures
for regsub in submodels:
    # Skip 'ocn' for now
    #if regsub == 'ocn':
    #    continue

    for cpusub in submodels:
        fig, ax = plt.subplots(1, 1, figsize=(6., 6.))

        if maintimes[regsub][cpusub]:
            peset = np.array(sorted(set(maintimes[regsub][cpusub].keys())))
        else:
            peset = np.array(sorted(set(subtimes[regsub][cpusub].keys())))

        pe_widths = [peset[i+1] - peset[i] for i in range(len(peset) - 1)]
        pe_widths.append(pe_widths[-1])
        pe_widths = np.array(pe_widths)

        pe_widths = 0.9 * pe_widths

        ax.set_xscale('log')
        ax.set_xlim(np.min(peset) / 1.1, np.max(peset) * 1.5)
        ax.set_xticks(peset + pe_widths / 2.)
        ax.set_xticklabels(peset)
        ax.set_ylim(0., 1.)
        ax.set_xlabel('# of CPUs')
        ax.set_ylabel('Relative runtime')
        ax.set_title('Relative runtime of main loop subroutines')
        ax.minorticks_off()

        ax.xaxis.label.set_color(ctxt)
        ax.yaxis.label.set_color(ctxt)
        ax.title.set_color(ctxt)
        for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
            label.set_color(ctxt)

        #----

        main_rt = np.zeros(len(peset))
        for i, pe in enumerate(peset):
            if regsub in inittimes:
                # Remove any initialization subroutines inside main function
                m_rt_pes = np.array([t for t in maintimes[regsub][cpusub][pe]])
                i_rt_pes = np.zeros(len(m_rt_pes))

                for subrt in init_subroutines[regsub]:
                    i_rt_pes += np.array([t for t in inittimes[regsub][cpusub][pe][subrt]])

                main_rt[i] = np.mean(m_rt_pes - i_rt_pes)
            elif maintimes[regsub][cpusub]:
                # Explicitly read the main subroutine time
                m_rt_pes = np.array([t for t in maintimes[regsub][cpusub][pe]])
                main_rt[i] = m_rt_pes.mean()
            else:
                # Assume the total equals the sum of subroutines
                for subrt in main_subroutines[regsub]:
                    main_rt[i] += np.mean([t for t in subtimes[regsub][cpusub][pe][subrt]])

        btm_bar = np.zeros(main_rt.shape)
        n_subrt = len(main_subroutines[regsub])
        #cm = plt.get_cmap('Set1')
        #colors = cm([1. * i / n_subrt for i in range(n_subrt)])

        handles = []
        #for subrt, c_subrt in zip(main_subroutines[regsub], colors):
        for subrt in main_subroutines[regsub]:

            subrt_times = np.array(
                    [np.mean([t for t in subtimes[regsub][cpusub][pe][subrt]])
                     for pe in peset]
            )

            #h = plt.bar(peset, subrt_times / main_rt, pe_widths, edgecolor='k',
            #            bottom=btm_bar, color=c_subrt, align='edge')
            h = plt.bar(peset, subrt_times / main_rt, pe_widths, edgecolor='k',
                        bottom=btm_bar, align='edge')
            btm_bar += subrt_times / main_rt

            handles.append(h)

        ax.legend(handles, main_subroutines[regsub], loc=(-1.0, 0.0), fontsize=9)
        #ax.legend(handles[::-1], main_subroutines[::-1], loc=(-0.6, 0.), fontsize=12)

        plt.savefig('barfigs/{}_vs_{}.svg'.format(regsub, cpusub),
                    facecolor='none', bbox_inches='tight')
        plt.close()
