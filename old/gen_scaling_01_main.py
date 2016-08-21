from collections import defaultdict
import os

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import numpy as np
import yaml

#formats= ('pdf', 'eps', 'svg', 'png'):
formats = ('svg', 'pdf', 'eps', 'jpg')

with open('timings01.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

prof_data = defaultdict(list)
for expt in timings:
    for run in timings[expt]:
        # Sort the entries
        run_rec = timings[expt][run]

        if run_rec['npernode'] == 12:
            prof_data['12ppn'].append(run_rec)
        elif run_rec['ht'] is True:
            prof_data['ht'].append(run_rec)
        else:
            prof_data['raijin'].append(run_rec)

# Keep the fastest run
for expt in prof_data:
    fastest = {}
    for run in prof_data[expt]:
        npes = run['npes']
        if (npes not in fastest
            or fastest[npes]['runtimes']['total'] > run['runtimes']['total']):
            fastest[npes] = run

    # Reconstruct prof_data entry:
    prof_data[expt] = [fastest[npes] for npes in fastest]

ncpus = {}
wtime = {}
speedup = {}    # Unused
effcy = {}

for p in prof_data:
    pdata = prof_data[p]
    wdata = sorted([(rec['npes'], rec['runtimes']['loop']) for rec in pdata])
    ncpus_raw, wtime_raw = zip(*wdata)

    ncpus[p] = np.array(ncpus_raw)
    wtime[p] = np.array(wtime_raw)
    speedup[p] = wtime[p][0] / np.array(wtime[p])   # Unused
    effcy[p] = ((ncpus[p][0] * wtime[p][0])
                    / (np.array(ncpus[p]) * np.array(wtime[p])))

# Wall time across platforms
fig, (ax_wt, ax_eff) = plt.subplots(1, 2, sharex=True, figsize=(14, 6))

xticks = ncpus['ht']
ax_eff.set_xlabel('Number of CPUs')

for ax in (ax_wt, ax_eff):
    # Disable default ticks
    ax.tick_params(axis='x',
                   which='minor',
                   bottom='off',
                   top='off',
                   labelbottom='off')

    ax.set_xscale('log')
    ax.set_xlim(600, 20500)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)

# Set up a logarithmic y axis
yticks = 500 * 2**np.arange(5)
ax_wt.tick_params(axis='y',
                  which='minor',
                  bottom='off',
                  top='off',
                  labelbottom='off')

ax_wt.set_yscale('log')
#ax_wt.set_ylim(400., 12000.)
ax_wt.set_yticks(yticks)
ax_wt.set_yticklabels(yticks)

ax_eff.set_ylim(0., 1.2)

ax_wt.set_title('Model runtime')
ax_wt.set_ylabel('Walltime (s)')

ax_eff.set_title('Scaling efficiency relative to 625 CPUs')
ax_eff.set_ylabel('Scaling efficiency')

ax_eff.axhline(1.0, color='k', linestyle='--')
ax_eff.axhline(0.8, color='k', linestyle=':', linewidth=0.5)

ax_data = {ax_wt: wtime,
           ax_eff: effcy}
ax_lines = {ax_wt: [],
            ax_eff: []}

titles = ['Default', 'Hyperthr.', '12 PPN', 'Ladder', 'Snake']
for ax in (ax_wt, ax_eff):
    for p in ('raijin', 'ht', '12ppn', 'ladder', 'snake'):
        try:
            ax_l, = ax.plot(ncpus[p], ax_data[ax][p], marker='+')
            ax_lines[ax].append(ax_l)
        except KeyError:
            pass

    #ax.legend(ax_lines[ax], titles, loc='best')

plt.tight_layout()
for ext in formats:
    plt.savefig('scaling01_main.{}'.format(ext))
