import os

import matplotlib.pyplot as plt
import numpy as np
import yaml

pdata_files = [
    'ladder.yaml',
    'snake.yaml'
]

#formats= ('pdf', 'eps', 'svg', 'png'):
formats = ('svg', 'pdf', 'eps')

platforms = [p.rstrip('.yaml') for p in pdata_files]

prof_data = {}
for platform, fname in zip(platforms, pdata_files):
    with open(os.path.join('old_timings', fname)) as pfile:
        prof_data[platform] = yaml.load(pfile)

ncpus = {}
wtime = {}
speedup = {}    # Unused
effcy = {}

for p in prof_data:
    pdata = prof_data[p]
    wdata = sorted([(n, pdata[n]['runtime']['total']) for n in pdata])
    ncpus_raw, wtime_raw = zip(*wdata)

    ncpus[p] = np.array(ncpus_raw)
    wtime[p] = np.array(wtime_raw)
    speedup[p] = wtime[p][1] / np.array(wtime[p])   # Unused
    effcy[p] = ((ncpus[p][1] * wtime[p][1])
                    / (np.array(ncpus[p]) * np.array(wtime[p])))

# Wall time across platforms
fig, (ax_wt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))

fig.suptitle('FX10 scaling', fontsize=16)

xticks = ncpus['ladder']
ax_eff.set_xlabel('Number of CPUs')

for ax in (ax_wt, ax_eff):
    # Disable default ticks
    ax.tick_params(axis='x',
                   which='minor',
                   bottom='off',
                   top='off',
                   labelbottom='off')

    ax.set_xscale('log')
    ax.set_xlim(100, 2000)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, rotation=30)
    ax.set_xlabel('# of CPUs')

ax_wt.set_ylim(1e3, 1e4)

ax_wt.set_yscale('log')
ax_wt.set_ylabel('Runtime (s)')
ax_wt.set_title('30-day runtime')

ax_eff.set_ylim(0., 1.1)
ax_eff.set_title('30-day efficiency')

ax_eff.axhline(1.0, color='k', linestyle='--')
ax_eff.axhline(0.8, color='k', linestyle=':', linewidth=0.5)

ax_data = {ax_wt: wtime,
           ax_eff: effcy}
ax_lines = {ax_wt: [],
            ax_eff: []}

# Plot theoretical speedup
p_ref = 160
pes = ncpus['snake']
rtdata = ax_data[ax_wt]['snake']

t_ref = rtdata[0]
t_opt = t_ref * p_ref / pes

ax_wt.plot(pes, t_opt, '-', color='k', linestyle='--')

titles = ['Ladder', 'Snake']
for ax in (ax_wt, ax_eff):
    for p in ('ladder', 'snake'):
        ax_l, = ax.plot(ncpus[p], ax_data[ax][p], marker='^', linestyle=':',
                        markeredgewidth=1, markersize=8)
        ax_lines[ax].append(ax_l)

ax_wt.legend(ax_lines[ax], titles, loc='best')

for ext in formats:
    plt.savefig('fx10_scaling.{}'.format(ext),
                facecolor='none', bbox_inches='tight')
