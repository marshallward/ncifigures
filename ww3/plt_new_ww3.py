from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg', 'pdf')
ctxt = 'k'

# Open MPI runtimes
with open('serial_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = defaultdict(list)

for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['ncpus']
        for key in timings[expt][run]['runtimes']:
            min_rt = timings[expt][run]['runtimes'][key]['min']
            mean_rt = timings[expt][run]['runtimes'][key]['mean']
            max_rt = timings[expt][run]['runtimes'][key]['max']
            std_rt = timings[expt][run]['runtimes'][key]['std']
            runtimes[key].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Plots
for fn_name in runtimes:
    rt = runtimes[fn_name]

    fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(fn_name, fontsize=16)
    #fig.suptitle(fn_name, fontsize=16, color='w')

    # Use one of the runtimes for configuration

    for ax in (ax_rt, ax_eff):
        ax.set_xscale('log')
        ax.set_xlim(0.8, 600)
        ax.set_xlabel('# of PEs')
        ax.set_xticks([pt[0] for pt in rt])
        ax.set_xticklabels([pt[0] for pt in rt], rotation=0)
        ax.minorticks_off()

        ## Set text color to white
        #ax.xaxis.label.set_color('w')
        #ax.yaxis.label.set_color('w')
        #ax.title.set_color('w')
        #for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        #    label.set_color('w')

    #----------------------
    # Runtime scaling plot

    if fn_name == 'w3wave':
        ax_rt.set_ylim(1e0, 1e4)
    else:
        ax_rt.set_ylim(1e-1, 1e3)
    ax_rt.set_yscale('log')
    ax_rt.set_title('10-day runtime')

    # Plot theoretical speedup
    p_ref = 8
    pes = np.array(sorted(list(set(pt[0] for pt in rt))))

    # Theoretical scaling line
    t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
    t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
    t_opt = t_ref * p_ref / pes

    ax_rt.plot(pes, t_opt, '--', color='k')

    for pt in rt:
        ax_rt.plot(pt[0], pt[1], 'o', markeredgewidth=1, markersize=8, color='b')
        ax_rt.plot(pt[0], pt[2], 'v', markeredgewidth=1, markersize=8, color='g')
        ax_rt.plot(pt[0], pt[3], '^', markeredgewidth=1, markersize=8, color='r')

    #----------------
    # Efficiency plot

    ax_eff.set_ylim(0., 1.5)
    ax_eff.set_title('Efficiency (w.r.t. {} PEs)'.format(p_ref))

    ax_eff.axhline(1., color='k', linestyle='--')
    ax_eff.axhline(0.8, color='k', linestyle=':')

    for pt in rt:
        ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1], 'o', color='r')

    for fmt in formats:
        plt.savefig('{}.{}'.format(fn_name, fmt),
                    facecolor='none', bbox_inches='tight')

    plt.close()
