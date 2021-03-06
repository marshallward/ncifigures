from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'w'
yrange = True
ymin, ymax = 1e-1, 1e3
submodels = ('atm', 'ocn', 'ice')

p_sub_ref = {
        'atm': 96,
        'ice': 96,
        'ocn': 240,
}

fn_ranges = {
        'atm_step_4a':          (1e1, 1e3),
        'ice_step':             (1e1, 1e3),
        'update_ocean_model':   (1e1, 1e3),
}

# Open MPI runtimes
with open('cm2.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = {}
for sub in submodels:
    runtimes[sub] = defaultdict(list)

for sub in submodels:
    for expt in timings:
        # Skip experiments with non-default scalings
        expt_sub = expt.split('_')[0]
        if expt_sub in submodels and expt_sub != sub:
            continue

        # Skip empty runs (e.g. dud postprocessing)
        if not 'runtimes' in timings[expt][sub]:
            continue

        npes = timings[expt][sub]['n']
        rt = timings[expt][sub]['runtimes']
        for key in rt:
            min_rt = rt[key]['min']
            mean_rt = rt[key]['mean']
            max_rt = rt[key]['max']
            std_rt = rt[key]['std']
            runtimes[sub][key].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Create figure directories
try:
    os.mkdir('figs')
except FileExistsError:
    pass

for sub in submodels:
    try:
        os.mkdir(os.path.join('figs', sub))
    except FileExistsError:
        pass

# Plots
for sub in submodels:
    for fn_name in runtimes[sub]:
        rt = runtimes[sub][fn_name]

        fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle(fn_name, color=ctxt)

        # Use one of the runtimes for configuration

        peset = sorted(set([pt[0] for pt in rt]))

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
        p_ref = p_sub_ref[sub]
        pes = np.array(sorted(list(set(pt[0] for pt in rt))))

        # Theoretical scaling line
        t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
        t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
        t_opt = t_ref * p_ref / pes

        ax_rt.plot(pes, t_opt, '--', color='k')

        for pt in rt:
            #ax_rt.plot(pt[0], pt[1], 'o', markeredgewidth=1, markersize=8, color='b')
            #ax_rt.plot(pt[0], pt[2], 'v', markeredgewidth=1, markersize=8, color='g')
            #ax_rt.plot(pt[0], pt[3], '^', markeredgewidth=1, markersize=8, color='r')

            errbar = np.array([[pt[1] - pt[2]], [pt[3] - pt[1]]])
            ax_rt.errorbar(pt[0], pt[1], yerr=errbar,
                           fmt='o', markeredgewidth=1, markeredgecolor='k',
                           markersize=8, color='r', ecolor='b')

        #----------------
        # Efficiency plot

        ax_eff.set_ylim(0., 1.2)
        ax_eff.set_title('Efficiency rel. to {} CPUs'.format(p_ref))

        for pt in rt:
            ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'o', color='r',
                        markeredgecolor='k')

        ax_eff.axhline(1., color='k', linestyle='--')
        ax_eff.axhline(0.8, color='k', linestyle=':')

        for fmt in formats:
            plt.savefig('figs/{}/{}.{}'.format(sub, fn_name, fmt),
                        facecolor='none', bbox_inches='tight')

        plt.close()
