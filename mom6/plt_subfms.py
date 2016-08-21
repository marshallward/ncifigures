from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
c_txt = 'k'

timings_files = {
    'mom5': 'mom5_fms_timings.yaml',
    'mom6': 'mom6_fms_timings.yaml'
}
models = list(timings_files.keys())

# Open MPI runtimes
timings = {}
for model in models:
    with open(timings_files[model], 'r') as tfile:
        timings[model] = yaml.load(tfile)

runtimes = {}
for model in models:
    runtimes[model] = defaultdict(list)

for model in models:
    for expt in timings[model]:
        for run in timings[model][expt]:
            npes = timings[model][expt][run]['npes']
            for key in timings[model][expt][run]['runtimes']:
                rt = timings[model][expt][run]['runtimes'][key]
                runtimes[model][key].append((npes, rt))

ref = {
    'mom5': 240,
    'mom6': 120,
}

mark = {
    'mom5': 'b',
    'mom6': 'r',
}

# Plots (only use abbreviated mom6 list)
for fn_name in runtimes['mom6']:
    print("plotting {}".format(fn_name))

    fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(fn_name, color=c_txt)

    peset = set()
    for model in models:
        peset = peset.union(set([pt[0] for pt in runtimes[model][fn_name]]))

    peset = sorted(peset)

    for ax in (ax_rt, ax_eff):

        ax.set_xscale('log')
        ax.set_xlim(50, 16000)
        ax.set_xlabel('# of PEs')
        ax.set_xticks(peset)
        ax.set_xticklabels(peset, rotation=30)
        ax.minorticks_off()

        # Set text color to white
        ax.xaxis.label.set_color(c_txt)
        ax.yaxis.label.set_color(c_txt)
        ax.title.set_color(c_txt)
        for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
            label.set_color(c_txt)

    #----------------------
    # Runtime scaling plot

    ax_rt.set_ylim(1e-1, 1e4)
    ax_rt.set_yscale('log')
    ax_rt.set_title('10-day runtime')

    for model in models:

        rt = runtimes[model][fn_name]

        # Use one of the runtimes for configuration

        # Plot theoretical speedup
        p_ref = ref[model]

        # Theoretical scaling line
        t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
        t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
        t_opt = t_ref * p_ref / peset

        ax_rt.plot(peset, t_opt, '--', color='k')

        for pt in rt:
            ax_rt.plot(pt[0], pt[1], 'o', markeredgewidth=1, markersize=8, color=mark[model])
            #ax_rt.plot(pt[0], pt[2], 'v', markeredgewidth=1, markersize=8, color='g')
            #ax_rt.plot(pt[0], pt[3], '^', markeredgewidth=1, markersize=8, color='r')

        #----------------
        # Efficiency plot

        ax_eff.set_ylim(0., 1.5)
        ax_eff.set_title('Efficiency (w.r.t. {} PEs)'.format(p_ref))

        for pt in rt:
            ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'o', color=mark[model])

        for fmt in formats:
            plt.savefig('{}.{}'.format(fn_name, fmt),
                        facecolor='none', bbox_inches='tight')

    plt.close()
