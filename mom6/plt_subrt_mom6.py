from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'k'
yrange = True

fn_ranges = {
        'update_ocean_model':   (1e1, 1e4)
}

# Open MPI runtimes
with open('mom6_scorep_timings.yaml', 'r') as timings_file:
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

try:
    os.mkdir('figs')
except FileExistsError:
    pass

# Plots
for fn_name in runtimes:
    rt = runtimes[fn_name]

    fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(fn_name, color=ctxt)

    # Use one of the runtimes for configuration

    peset = sorted(set([pt[0] for pt in rt]))

    for ax in (ax_rt, ax_eff):
        ax.set_xscale('log')
        ax.set_xlim(50, 4500)
        ax.set_xlabel('# of CPUs')
        ax.set_xticks(peset)
        ax.set_xticklabels(peset, rotation=30)
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

    #if fn_name in fn_ranges:
    #    ys, ye = fn_ranges[fn_name]
    #else:
    #    ys, ye = 1e-1, 1e3

    if yrange:
        ys, ye = 1e0, 1e4
        ax_rt.set_ylim(ys, ye)

    ax_rt.set_yscale('log')
    ax_rt.set_title('10-day runtime')

    # Plot theoretical speedup
    p_ref = 60
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
                       fmt='o', markeredgewidth=1, markersize=8, color='r',
                       ecolor='b')

    #----------------
    # Efficiency plot

    ax_eff.set_ylim(0., 1.2)
    ax_eff.set_title('Efficiency rel. to {} CPUs'.format(p_ref))

    for pt in rt:
        ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'o', color='r')

    ax_eff.axhline(1., color='k', linestyle='--')
    ax_eff.axhline(0.8, color='k', linestyle=':')

    for fmt in formats:
        plt.savefig('figs/{}.{}'.format(fn_name, fmt),
                    facecolor='none', bbox_inches='tight')

    plt.close()
