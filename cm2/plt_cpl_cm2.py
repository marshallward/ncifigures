from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy
import yaml

formats = ('svg',)
ctxt = 'k'
yrange = True
ymin, ymax = 1e-1, 1e3
submodels = ('atm', 'ocn', 'ice')

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
        'ocn': 'main_mom'
}

main_subroutines = {}

main_subroutines['atm'] = [
        'atm_step_4a',
        'oasis3_geto2a',
        'oasis3_puta2o',
]

main_subroutines['ocn'] = [
        #'main_IP_ice_ocn_bnd_from_data',
        'main_IP_external_coupler_sbc_before',
        'update_ocean_model',
        'main_IP_external_coupler_sbc_after',
]

fn_ranges = {
        'main_um':              (1e1, 1e3),
        'cice_run':             (1e1, 1e3),
        'main_mom':             (1e1, 1e3),
        'atm_step_4a':          (1e1, 1e3),
        'ice_step':             (1e1, 1e3),
        'update_ocean_model':   (1e1, 1e3),
        'oasis3_geto2a':        (1e1, 1e3),
        'main_IP_external_coupler_sbc_after':   (1e1, 1e3),
}

with open('cm2.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

# Create some dummy regions to be populated by the script
for expt in timings:

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

    #timings[expt]['ocn']['runtimes']['main_um'] = {}
    #for key in ('mean', 'min', 'max', 'std'):
    #    timings[expt]['ocn']['runtimes']['main_mom'][key] = -1


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

        #expt_sub = expt.split('_')[0]
        #if expt_sub in submodels and expt_sub != sub:
        #    continue

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


print(runtimes['atm'].keys())

## Open MPI runtimes
#with open('cm2.yaml', 'r') as timings_file:
#    timings = yaml.load(timings_file)
#
#runtimes = {}
#for sub in submodels:
#    runtimes[sub] = defaultdict(list)
#
#for sub in submodels:
#    for expt in timings:
#        # Skip experiments with non-default scalings
#        expt_sub = expt.split('_')[0]
#        if expt_sub in submodels and expt_sub != sub:
#            continue
#
#        # Skip empty runs (e.g. dud postprocessing)
#        if not 'runtimes' in timings[expt][sub]:
#            continue
#
#        npes = timings[expt][sub]['n']
#        rt = timings[expt][sub]['runtimes']
#        for key in rt:
#            min_rt = rt[key]['min']
#            mean_rt = rt[key]['mean']
#            max_rt = rt[key]['max']
#            std_rt = rt[key]['std']
#            runtimes[sub][key].append((npes, mean_rt, min_rt, max_rt, std_rt))

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
            else:
                ys, ye = ymin, ymax

            ax_rt.set_ylim(ys, ye)

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
