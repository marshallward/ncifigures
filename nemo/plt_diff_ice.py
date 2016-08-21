from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg',)
ctxt = 'k'

timing_files = {
    'mom':  'mom_timings.yaml',
    'nemo': 'orca_scorep_timings.yaml',
    'mom6': 'mom6_scorep_timings.yaml',
}
models = ['nemo', 'mom', 'mom6']

# Open MPI runtimes
timings = {}
for model in models:
    with open(timing_files[model], 'r') as timing_file:
        timings[model] = yaml.load(timing_file)

runtimes = {}
for model in models:
    runtimes[model] = defaultdict(list)

#for model in models:
for model in ('nemo',):
    for expt in timings[model]:
        for run in timings[model][expt]:
            npes = timings[model][expt][run]['npes']
            for key in timings[model][expt][run]['runtimes']:
                min_rt = timings[model][expt][run]['runtimes'][key]['min']
                mean_rt = timings[model][expt][run]['runtimes'][key]['mean']
                max_rt = timings[model][expt][run]['runtimes'][key]['max']
                std_rt = timings[model][expt][run]['runtimes'][key]['std']
                runtimes[model][key].append((npes, mean_rt, min_rt, max_rt, std_rt))

try:
    os.mkdir('figs')
except FileExistsError:
    pass

# SIS2 seems very sensitive to Score-P so we can't append non-scorep results

# MOM6 7680 CPU didn't work with Score-P, so append those values here:
with open('mom6_fms_timings.yaml') as timings_file:
    fms_timings = yaml.load(timings_file)

# Set min/max/mean/std to the same value, to trick the rest of the code below
for expt in fms_timings:
    for run in fms_timings[expt]:
        npes = fms_timings[expt][run]['npes']
        #if not npes in (7680, 15360):
        #    continue
        min_rt = fms_timings[expt][run]['runtimes']['ice']
        mean_rt = fms_timings[expt][run]['runtimes']['ice']
        max_rt = fms_timings[expt][run]['runtimes']['ice']
        std_rt = fms_timings[expt][run]['runtimes']['ice']
        runtimes['mom6']['update_ice_model_slow_dn'].append((npes, mean_rt, min_rt, max_rt, std_rt))

# Ditto with MOM5 and 15360 CPUs
with open('mom5_fms_timings.yaml') as timings_file:
    fms_timings = yaml.load(timings_file)

# Set min/max/mean/std to the same value, to trick the rest of the code below
for expt in fms_timings:
    for run in fms_timings[expt]:
        npes = fms_timings[expt][run]['npes']
        #if not npes == 15360:
        #    continue
        min_rt = fms_timings[expt][run]['runtimes']['ice']
        mean_rt = fms_timings[expt][run]['runtimes']['ice']
        max_rt = fms_timings[expt][run]['runtimes']['ice']
        std_rt = fms_timings[expt][run]['runtimes']['ice']
        runtimes['mom']['update_ice_model_slow_dn'].append((npes, mean_rt, min_rt, max_rt, std_rt))

fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))

fn_diff = {
    'mom': 'update_ice_model_slow_dn',
    'nemo': 'sbc_ice_lim_2',
    'mom6': 'update_ice_model_slow_dn',
}

mcolor = {
    'mom': 'orange',
    'nemo': 'purple',
    'mom6': 'green',
}

mstyle = {
    'mom': 'd',
    'nemo': 'o',
    'mom6': '^',
}

mref = {
    'mom': 120,
    'nemo': 60,
    'mom6': 60,
}

lines = {}

# TODO union of mom and nemo peset

peset = set()
for model in models:
    peset = peset.union(set([pt[0] for pt in runtimes[model][fn_diff[model]]]))

peset = sorted(peset)

for model in models:
    fn_name = fn_diff[model]
    rt = runtimes[model][fn_name]

    # XXX: don't double-plot the axes
    for ax in (ax_rt, ax_eff):
        ax.set_xscale('log')
        ax.set_xlim(0.8 * min(peset), 1.2 * max(peset))
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

    ax_rt.set_ylim(1e0, 1e4)
    ax_rt.set_yscale('log')
    ax_rt.set_title('10-day runtime')

    # Plot theoretical speedup
    p_ref = mref[model]
    pes = np.array(sorted(list(set(pt[0] for pt in rt))))

    # Theoretical scaling line
    t_ref = np.mean([pt[1] for pt in rt if pt[0] == p_ref])
    t_min = np.min([pt[1] for pt in rt if pt[0] == p_ref])
    t_opt = t_ref * p_ref / pes

    ax_rt.plot(pes, t_opt, '--', color=mcolor[model])

    for pt in rt:
        lines[model], = ax_rt.plot(pt[0], pt[1],
                                   mstyle[model],
                                   markerfacecolor=mcolor[model],
                                   markeredgewidth=1, markersize=8)
        #ax_rt.plot(pt[0], pt[2], 'v', markeredgewidth=1, markersize=8, color='g')
        #ax_rt.plot(pt[0], pt[3], '^', markeredgewidth=1, markersize=8, color='r')

    #----------------
    # Efficiency plot

    ax_eff.set_ylim(0., 1.2)
    ax_eff.set_title('Efficiency')

    for pt in rt:
        ax_eff.plot(pt[0], t_min * p_ref / pt[0] / pt[1],
                    marker=mstyle[model], markerfacecolor=mcolor[model],
                    markersize=8, markeredgewidth=1)

    ax_eff.axhline(1., color='k', linestyle='--')
    ax_eff.axhline(0.8, color='k', linestyle=':')

ax_rt.legend((lines['nemo'], lines['mom'], lines['mom6']),
             ('LIM 2', 'SIS', 'SIS 2'), numpoints=1)

plt.savefig('mom_nemo_ice.svg', facecolor='none', bbox_inches='tight')
plt.close()
