import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# CPU count
ncpus = np.array([120, 240, 480, 960, 1440, 1920])

# Run labels
wt_labels = ['OpenMPI 1.8', 'Hyperthreaded', '12 cores per node']

# Walltimes
wt_default = np.array([5298., 2558., 1469., 1151., 1265., 1810.])
wt_ht = np.array([5220., 2393., 1221., 707., 573., 480.])
wt_12ppn = np.array([4112., 1970., 1013., 583., 469., 419.])

# % MPI communication time
comm_default = [19.0, 23.1, 35.3, 57.4, 70.1, 65.4]
comm_ht = [17.6, 17.5, 20.7, 27.1, 27.9, 27.8]
comm_12ppm = [15.2, 16.9, 18.9, 22.5, 25.9, 26.3]

# Memory usage
mem_usage = [1.7, 1.0, 0.72, 0.70, 0.82, 0.94]
mem_limit = 2.0

# Collect datasets
walltimes = [wt_default, wt_ht, wt_12ppn]
speedups = [ [wt[1] / w for w in wt] for wt in walltimes]
comms = [comm_default, comm_ht, comm_12ppm]

datasets = [walltimes, speedups, comms]

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()

axes = (ax1, ax2, ax3, ax4)

#ax1.set_xscale('log')
#ax3.set_xscale('log')
#ax4.set_xscale('log')

for ax in axes:

    if ax != ax2:
        ax.set_xscale('log')

    ax.tick_params(axis='x',
                   which='minor',
                   bottom='off',
                   top='off',
                   labelbottom='off')
    ax.set_xticks(ncpus)
    ax.set_xticklabels(ncpus)

    ax.set_xlim([100, 2200])

    ax.set_xlabel('Number of CPUs')
    ax.set_ylabel('Walltime (sec)')

ax1.set_title('1-Month Walltime')
ax2.set_title('Speedup')
ax3.set_title('% MPI Comm time')
ax4.set_title('Memory usage per core')

ax1.set_ylim([0., 5500.])
ax2.set_ylim([0., 8.])
ax3.set_ylim([0., 100.])
ax4.set_ylim([0., 2.2])

for (ax, groups) in zip(axes[:3], datasets):
    for ts in groups:
        ax.plot(ncpus, ts,
                 linestyle=':',
                 marker='x',
                 markersize=10.,
                 markeredgewidth=2.)

ax2.plot(ncpus, ncpus / ncpus[1], color='k')

ax4.plot(ncpus, mem_usage,
         linestyle=':',
         marker='x',
         markersize=10.,
         markeredgewidth=2.)
ax4.axhline(mem_limit, linestyle='--')

for ax in axes[:3]:
    ax.legend(wt_labels, loc='best')

fig1.savefig('walltime.svg')
fig2.savefig('speedup.svg')
fig3.savefig('mpicomm.svg')
fig4.savefig('memusage.svg')

fig1.savefig('walltime.pdf')
fig2.savefig('speedup.pdf')
fig3.savefig('mpicomm.pdf')
fig4.savefig('memusage.pdf')
