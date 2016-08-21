from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

formats = ('svg', 'pdf')
tname = 'loop'

# Concurrent timings
with open('cc_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['ice_npes']
        time = timings[expt][run]['runtimes'][tname]
        runtimes.append((npes, time))

# Serial timings
with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

serial_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        if npes == 960:
            time = timings[expt][run]['runtimes'][tname]
            serial_runtimes.append(time)

fig, (ax_960, ax_1920) = plt.subplots(1, 2, figsize=(12., 6.))

for ax in (ax_960, ax_1920):
    ax.set_xscale('log')
    ax.set_xlabel('Sea Ice PEs')
    ax.set_xlim(20, 2000)

    ax.set_yscale('log')
    ax.set_ylabel('Runtime (s)')
    ax.set_ylim(1e1, 1e3)

    # Set text color to white
    ax.xaxis.label.set_color('w')
    ax.yaxis.label.set_color('w')
    ax.title.set_color('w')
    for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color('w')

pes = sorted(list(set(pt[0] for pt in runtimes)))
ax_960.set_xticks(pes)
ax_960.set_xticklabels(pes, rotation=45)
#ax_960.set_ylim(100, 1000)

if tname == 'total':
    ax_960.axhline(min(serial_runtimes), linestyle='--', color='k')
    ax_960.axhline(sum(serial_runtimes) / len(serial_runtimes), color='k')
    ax_960.axhline(max(serial_runtimes), linestyle='--', color='k')
else:
    ax_960.axhline(sum(serial_runtimes) / len(serial_runtimes), linestyle='--',
                   color='k')

for pt in runtimes:
    ax_960.plot(pt[0], pt[1], '^', color='r', markeredgewidth=1, markersize=8)

ax_960.set_title('960 Ocean PEs')

# Diagnostic check
rt = defaultdict(list)
for pt in runtimes:
    rt[pt[0]].append(pt[1])

# Concurrent timings
with open('cch_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['ice_npes']
        time = timings[expt][run]['runtimes'][tname]
        runtimes.append((npes, time))

# Serial timings
with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

serial_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        if npes == 1920:
            time = timings[expt][run]['runtimes'][tname]
            serial_runtimes.append(time)

pes = sorted(list(set(pt[0] for pt in runtimes)))
ax_1920.set_xticks(pes)
ax_1920.set_xticklabels(pes, rotation=45)

if tname == 'total':
    ax_1920.axhline(min(serial_runtimes), linestyle='--', color='k')
    ax_1920.axhline(sum(serial_runtimes) / len(serial_runtimes), color='k')
    ax_1920.axhline(max(serial_runtimes), linestyle='--', color='k')
else:
    ax_1920.axhline(sum(serial_runtimes) / len(serial_runtimes),
                    linestyle='--', color='k')

for pt in runtimes:
    ax_1920.plot(pt[0], pt[1], '^', color='r', markeredgewidth=1, markersize=8)

ax_1920.set_title('1920 Ocean PEs')

# Diagnostic check
rt = defaultdict(list)
for pt in runtimes:
    rt[pt[0]].append(pt[1])

for ax in (ax_960, ax_1920):
    ax.minorticks_off()

for fmt in formats:
    plt.savefig('loop.{}'.format(fmt), facecolor='none', bbox_inches='tight')
