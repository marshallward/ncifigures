from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy
import yaml

cm2_file = 'cm2_oasis.yaml'
formats = ('svg',)
ctxt = 'w'
yrange = True
ymin, ymax = 1e-1, 1e3
submodels = ('atm', 'ocn', 'ice')
adjust_runtimes = True

# CPU stats

np_default = {
        'atm': 432,
        'ice': 192,
        'ocn': 960
}

p_sub_ref = {
        'atm': 96,
        'ice': 96,
        'ocn': 240,
}

# Regions

regions = [
    # Mains
    'main_um',
    'main_cice',
    'main_mom',
    'cice_run',
    # Coupling
    'oasis3_geto2a',
    'oasis3_puta2o',
    'from_coupler',
    'from_atm',
    'from_ocn',
    'into_atm',
    'into_ocn',
    'main_IP_external_coupler_sbc_before',
    'main_IP_external_coupler_sbc_after',
]

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
        'incrtime',
        'oasis3_geto2a',
        'atm_step_4a',
        'settsctl',
        'ukca_main1',
        'oasis3_puta2o',
]

main_subroutines['ice'] = [
        'cice_run',
]

main_subroutines['ocn'] = [
        'mpp_clock_begin',
        'main_IP_external_coupler_sbc_before',
        'update_ocean_model',
        'main_IP_external_coupler_sbc_after',
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


fn_ranges = {
        'main_um':              (1e1, 1e3),
        'main_cice':            (1e1, 1e3),
        'main_mom':             (1e1, 1e3),
        'atm_step_4a':          (1e1, 1e3),
        'cice_run':             (1e1, 1e3),
        'ice_step':             (1e1, 1e3),
        'update_ocean_model':   (1e1, 1e3),
        'oasis3_geto2a':        (1e0, 1e3),
        'main_IP_external_coupler_sbc_after':   (1e0, 1e3),
        'into_atm':             (1e0, 1e2),
        'from_ocn':             (1e0, 1e3),
        'from_atm':             (1e-1, 1e3),
}

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
    # (try to correct for oasis wait times due to initialization)
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

    # Main runtime diagnostic
    for sub in main_regions:
        print(expt, timings[expt][sub]['runtimes'][main_regions[sub]]['mean'])

# Call regions are encapsulated by submodel, though maybe this is unncessary...
# If unnecessary, then just do runtimes = defaultdict(list)
runtimes = {}
for sub in submodels:
    runtimes[sub] = defaultdict(list)

for expt in timings:
    ncpus = {}
    for sub in submodels:
        # Only makes sense to exclude other submodels for intrinsic stuff
        # Don't do this for "coupled" subroutines

        ncpus[sub] = timings[expt][sub]['n']

        rt = timings[expt][sub]['runtimes']
        for key in rt:
            # Skip if not in region whitelist (otherwise it's too slow)
            if key not in regions:
                continue

            min_rt = rt[key]['min']
            mean_rt = rt[key]['mean']
            max_rt = rt[key]['max']
            std_rt = rt[key]['std']
            runtimes[sub][key].append((ncpus, mean_rt, min_rt, max_rt, std_rt))


# Create figure directories
try:
    os.mkdir('cplfigs')
except FileExistsError:
    pass

for sub in submodels:
    try:
        os.mkdir(os.path.join('cplfigs', sub))
    except FileExistsError:
        pass

# Plots
for regsub in submodels:
    for fn_name in runtimes[regsub]:
        for cpusub in submodels:
            # Skip non-default CPU size for other submodels
            rt = runtimes[regsub][fn_name]

            fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
            fig.suptitle('{} ({})'.format(fn_name, cpusub), color=ctxt)

            # Use one of the runtimes for configuration

            peset = sorted(set([pt[0][cpusub] for pt in rt]))

            for ax in (ax_rt, ax_eff):
                ax.set_xscale('log')
                ax.set_xlim(min(peset) / 1.1, max(peset) * 1.1)
                ax.set_xlabel('# of CPUs')
                ax.set_xticks(peset)
                ax.set_xticklabels(peset, rotation=45)
                #ax.set_xticks([pt[0] for pt in rt])
                #ax.set_xticklabels([pt[0] for pt in rt], rotation=30)
                ax.minorticks_off()

                # Set text color to white
                ax.xaxis.label.set_color(ctxt)
                ax.yaxis.label.set_color(ctxt)
                ax.title.set_color(ctxt)
                for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
                    label.set_color(ctxt)

            #----------------------
            # Runtime scaling plot

            if fn_name in fn_ranges:
                ys, ye = fn_ranges[fn_name]
                ax_rt.set_ylim(ys, ye)
            else:
                ys, ye = ymin, ymax

            #ax_rt.set_ylim(ys, ye)

            ax_rt.set_yscale('log')
            ax_rt.set_title('10-day runtime')

            # Plot theoretical speedup
            p_ref = p_sub_ref[cpusub]
            pes = numpy.array(sorted(list(set(pt[0][cpusub] for pt in rt))))

            # Theoretical scaling line
            t_ref = numpy.mean([pt[1] for pt in rt if pt[0][cpusub] == p_ref])
            t_min = numpy.min([pt[1] for pt in rt if pt[0][cpusub] == p_ref])
            t_opt = t_ref * p_ref / pes

            ax_rt.plot(pes, t_opt, '--', color='k')

            for pt in rt:
                # Skip non-default layouts in other submodels
                if any(pt[0][sub] != np_default[sub]
                       for sub in submodels if sub != cpusub):
                    continue

                np = pt[0][cpusub]

                #ax_rt.plot(pt[0], pt[1], 'o', markeredgewidth=1, markersize=8, color='b')
                #ax_rt.plot(pt[0], pt[2], 'v', markeredgewidth=1, markersize=8, color='g')
                #ax_rt.plot(pt[0], pt[3], '^', markeredgewidth=1, markersize=8, color='r')

                errbar = numpy.array([[pt[1] - pt[2]], [pt[3] - pt[1]]])
                ax_rt.errorbar(np, pt[1], yerr=errbar,
                               fmt='o', markeredgewidth=1, markeredgecolor='k',
                               markersize=8, color='r', ecolor='b')

            #----------------
            # Efficiency plot

            ax_eff.set_ylim(0., 1.2)
            ax_eff.set_title('Efficiency rel. to {} CPUs'.format(p_ref))

            for pt in rt:
                # Skip non-default layouts in other submodels
                if any(pt[0][sub] != np_default[sub]
                       for sub in submodels if sub != cpusub):
                    continue

                np = pt[0][cpusub]
                ax_eff.plot(np, t_min * p_ref / np / pt[1], 'o', color='r',
                            markeredgecolor='k')

            ax_eff.axhline(1., color='k', linestyle='--')
            ax_eff.axhline(0.8, color='k', linestyle=':')

            for fmt in formats:
                plt.savefig('cplfigs/{}/{}_{}.{}'.format(regsub, fn_name, cpusub, fmt),
                            facecolor='none', bbox_inches='tight')

            plt.close()
