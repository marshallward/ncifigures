from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

cm2_file = 'cm2_oasis.yaml'
formats = ('svg',)
ctxt = 'k'
submodels = ('atm', 'ocn', 'ice')
default_ncpus = {
        'atm': 432,
        'ice': 192,
        'ocn': 960,
}
adjust_runtimes = True

main_regions = {
        'atm': 'main_um',
        'ice': 'main_cice',
        'ocn': 'main_mom'
}

init_regions = {
        'atm': 'init_um',
        'ice': 'init_cice',
        'ocn': 'init_mom'
}


main_subroutines = {}
init_subroutines = {}

main_subroutines['atm'] = [
        'atm_step_4a',
        'oasis3_geto2a',
        'oasis3_puta2o',
        'incrtime',
        'settsctl',
        'ukca_main1',
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
        'update_ocean_model',
        'main_IP_external_coupler_sbc_after',
        'main_IP_external_coupler_sbc_before',
        'mpp_clock_begin',
]

init_subroutines['atm'] = [
        'oasis_initialise',
        'initial_4a',
]

init_subroutines['ice'] = [
        'cice_initialize',
]


init_subroutines['ocn'] = [
        'main_IP_external_coupler_sbc_init',
        'main_IP_external_coupler_mpi_init',
        'ocean_model_init',
        'fms_init',
]

with open(cm2_file, 'r') as timings_file:
    timings = yaml.load(timings_file)

# Create some dummy regions to be populated by the script
for expt in timings:

    # TODO: Combine with main
    for sub in init_regions:
        timings_rt = timings[expt][sub]['runtimes']

        init_reg = init_regions[sub]

        timings_rt[init_reg] = {}
        for key in ('mean', 'min', 'max'):
            timings_rt[init_reg][key] = 0.
            for reg in init_subroutines[sub]:
                rt = timings_rt[reg][key]
                timings_rt[init_reg][key] += rt
        timings_rt[init_reg]['std'] = -1   # root mean square?

    # Main time adjustment
    if adjust_runtimes:
        # Remove restart IO write time
        io_reg = 'oasis_io_write_avfile'

        for msub in ('atm', 'ice'):
            if msub == 'atm':
                cpl_regs = ['oasis3_puta2o']
            elif msub == 'ice':
                cpl_regs = ['into_atm', 'cice_run']
            else:
                print('oh no!')
                sys.exit(-1)

            io_rt = timings[expt][msub]['runtimes'][io_reg]['mean']
            for key in ('mean', 'min', 'max'):
                for creg in cpl_regs:
                    main_rt = timings[expt][msub]['runtimes'][creg][key]
                    timings[expt][msub]['runtimes'][creg][key] = main_rt - io_rt

        # Get initialisation times
        init_rts = {sub: timings[expt][sub]['runtimes'][init_regions[sub]]['mean']
                    for sub in submodels}
        max_sub = max(init_rts, key=init_rts.get)
        max_rt = init_rts[max_sub]

        a_rt, i_rt, o_rt = (init_rts[s] for s in ('atm', 'ice', 'ocn'))

        # Ocean initialization lag adjust
        if o_rt < i_rt:
            d_rt = i_rt - o_rt

            reg = 'main_IP_external_coupler_sbc_after'
            o2i_rt = timings[expt]['ocn']['runtimes'][reg]['mean']

            # Ocn does 3 hrs of steps before receiving (1/8 of rt)
            rt_steps = timings[expt]['ocn']['runtimes']['update_ocean_model']['mean']
            step_rt = rt_steps / 8.

            # NOTE: The max(,0) check is most likely due to IO diff
            #       This only seems to occur when the diff is small (i.e. IO)
            diff_rt_raw = o2i_rt - d_rt + step_rt
            if diff_rt_raw < 0:
                print('warning: negative runtime')
            diff_rt = max(diff_rt_raw, 0)

            timings[expt]['ocn']['runtimes'][reg]['mean'] = diff_rt
            for val in ('min', 'max'):
                val_rt = timings[expt]['ocn']['runtimes'][reg][val]
                new_val_rt = max(val_rt - d_rt + step_rt, 0)
                timings[expt]['ocn']['runtimes'][reg][val] = new_val_rt
        else:
            reg = 'from_ocn'
            i2o_rt = timings[expt]['ice']['runtimes'][reg]['mean']
            d_rt = o_rt - i_rt

            diff_rt = i2o_rt - d_rt
            timings[expt]['ice']['runtimes'][reg]['mean'] = diff_rt
            for val in ('min', 'max'):
                val_rt = timings[expt]['ice']['runtimes'][reg][val]
                timings[expt]['ice']['runtimes'][reg][val] = max(val_rt - d_rt, 0)

        # Atm initialization lag adjust
        if a_rt < i_rt or a_rt < o_rt:
            reg = 'oasis3_geto2a'
            i2a_rt = timings[expt]['atm']['runtimes'][reg]['mean']

            if i_rt < o_rt:
                d_rt = o_rt - a_rt
            else:
                d_rt = i_rt - a_rt

            # Atm does 3 hrs of steps before second recv (first is from file)
            step_rt = timings[expt]['atm']['runtimes']['atm_step_4a']['mean'] / 8.

            diff_rt = max(i2a_rt - d_rt + step_rt, 0)

            # Using max(,0) until actual differential is worked out...
            timings[expt]['atm']['runtimes'][reg]['mean'] = diff_rt
            for val in ('min', 'max'):
                val_rt = timings[expt]['atm']['runtimes'][reg][val]
                new_val_rt = max(val_rt - d_rt + step_rt, 0)
                timings[expt]['atm']['runtimes'][reg][val] = new_val_rt

    for sub in main_regions:
        timings_rt = timings[expt][sub]['runtimes']

        mreg = main_regions[sub]

        timings_rt[mreg] = {}
        for key in ('mean', 'min', 'max'):
            timings_rt[mreg][key] = 0.
            for reg in main_subroutines[sub]:
                rt = timings_rt[reg][key]
                timings_rt[mreg][key] += rt
        timings_rt[mreg]['std'] = -1   # root mean square?


maintimes = {}
subtimes = {}

for regsub in submodels:
    maintimes[regsub] = {}
    subtimes[regsub] = {}

    for cpusub in submodels:
        maintimes[regsub][cpusub] = {}
        subtimes[regsub][cpusub] = {}

inittimes = {}
#inittimes['atm'] = {}
#for cpusub in submodels:
#    inittimes['atm'][cpusub] = {}


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

            if regsub in main_regions:
                main_reg = main_regions[regsub]
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
        pe_widths.append(2. * pe_widths[-1])
        pe_widths = np.array(pe_widths)

        pe_widths = 0.9 * pe_widths

        ax.set_xscale('log')
        ax.set_xlim(np.min(peset) - 0.125 * pe_widths[0],
                    np.max(peset) + 1.25 * pe_widths[-1])
        ax.set_xticks(peset + pe_widths / 2.)
        ax.set_xticklabels(peset)
        #ax.set_ylim(0., 1.)
        ax.set_xlabel('# of {} CPUs'.format(cpusub))
        ax.set_ylabel('Relative runtime')
        ax.set_title('Relative runtime of {} main loop subroutines'.format(regsub))
        ax.minorticks_off()

        ax.xaxis.label.set_color(ctxt)
        ax.yaxis.label.set_color(ctxt)
        ax.title.set_color(ctxt)
        for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
            label.set_color(ctxt)

        #----

        main_rt = np.zeros(len(peset))
        for i, pe in enumerate(peset):
            #if regsub in inittimes:
            #    print('init times?')
            #    # Remove any initialization subroutines inside main function
            #    m_rt_pes = np.array([t for t in maintimes[regsub][cpusub][pe]])
            #    i_rt_pes = np.zeros(len(m_rt_pes))

            #    for subrt in init_subroutines[regsub]:
            #        i_rt_pes += np.array([t for t in inittimes[regsub][cpusub][pe][subrt]])

            #    main_rt[i] = np.mean(m_rt_pes - i_rt_pes)
            #elif maintimes[regsub][cpusub]:
            #    # Explicitly read the main subroutine time
            #    m_rt_pes = np.array([t for t in maintimes[regsub][cpusub][pe]])
            #    main_rt[i] = m_rt_pes.mean()
            #else:
            #    # Assume the total equals the sum of subroutines
            #    for subrt in main_subroutines[regsub]:
            #        main_rt[i] += np.mean([t for t in subtimes[regsub][cpusub][pe][subrt]])
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

            # Re-plot hatches
            for i, pe in enumerate(peset):
                if pe == default_ncpus[cpusub]:
                    pe_h = pe
                    rt_h = subrt_times[i] / main_rt[i]
                    pew_h = pe_widths[i]
                    btm_h = btm_bar[i]

                    plt.bar(pe_h, rt_h, pew_h, color='none', bottom=btm_h,
                            align='edge', hatch='x')

            btm_bar += subrt_times / main_rt

            handles.append(h)

        #ax.legend(handles, main_subroutines[regsub], loc=(-0.5, 0.0), fontsize=9)
        ax.legend(handles, main_subroutines[regsub], loc='best', fontsize=9)

        plt.savefig('barfigs/{}_vs_{}.svg'.format(regsub, cpusub),
                    facecolor='none', bbox_inches='tight')
        plt.close()
