from collections import defaultdict
import itertools
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import yaml

ctxt = 'k'

runtimes = {}

runtimes[480] = {}
runtimes[480]['ocn'] = (566.4, 567.4, 566.0, 568.0, 568.7, 570.9, 568.7)
runtimes[480]['ice'] = (237.1, 235.9, 240.9, 334.6, 357.8, 342.4, 395.5)
runtimes[480]['ocp'] = ( 60.3,  57.4,  57.6,  69.8,  78.4,  74.6, 100.0)
runtimes[480]['icp'] = (340.1, 338.8, 332.8, 255.3, 238.9, 251.3, 224.1)

runtimes[660] = {}
runtimes[660]['ocn'] = (433.5, 434.5, 434.7, 435.7, 434.0, 433.9, 435.7)
runtimes[660]['ice'] = (240.5, 347.7, 357.5, 302.1, 378.2, 404.4, 477.1)
runtimes[660]['ocp'] = ( 68.9,  95.1,  98.9, 105.4, 115.4, 132.0, 175.7)
runtimes[660]['icp'] = (209.1, 129.7, 124.9, 187.9, 117.4, 110.6,  77.6)

runtimes[720] = {}
runtimes[720]['ocn'] = (387.8, 391.0, 389.2, 390.2, 394.2, 390.3, 391.6)
runtimes[720]['ice'] = (250.5, 244.0, 253.1, 255.4, 363.1, 358.3, 373.0)
runtimes[720]['ocp'] = ( 68.2,  68.9,  73.5,  79.5, 110.9, 121.2, 123.5)
runtimes[720]['icp'] = (152.9, 164.8, 159.9, 160.5,  87.0,  88.6,  87.3)

runtimes[960] = {}
runtimes[960]['ocn'] = (304.2, 309.5, 305.2, 309.0, 309.7, 305.3, 310.6)
runtimes[960]['ice'] = (223.8, 231.4, 331.3, 327.5, 342.3, 348.5, 357.9)
runtimes[960]['ocp'] = ( 81.6,  92.2, 130.1, 133.7, 138.9, 149.8, 162.5)
runtimes[960]['icp'] = ( 85.4,  90.4,  33.7,  36.2,  37.2,  34.1,  35.2)

runtimes[1440] = {}
runtimes[1440]['ocn'] = (215.8, 215.0, 222.7, 231.6, 217.2, 224.9)
runtimes[1440]['ice'] = (233.7, 229.1, 232.2, 333.3, 323.3, 338.0)
runtimes[1440]['ocp'] = (174.5, 174.8, 194.3, 192.1, 210.5, 213.0)
runtimes[1440]['icp'] = ( 15.2,  14.9,  18.1,  13.1,  12.0,  14.0)


#-------------
formats = ('pdf', 'svg')

fig, (ax_mdl, ax_cpl) = plt.subplots(1, 2, figsize=(12, 6))

#fig, (ax_rt, ax_eff) = plt.subplots(1, 2, figsize=(12, 6))
#fig.suptitle('Main loop scaling', fontsize=16, color='w')

for ax in (ax_mdl, ax_cpl):
    ax.minorticks_off()

    ax.set_xlabel('# of CPUs')
    ax.set_xlim(400, 1500)
    ax.set_xticks([pe for pe in runtimes])
    ax.set_xticklabels([pe for pe in runtimes], rotation=45)
    ax.set_ylabel('Runtime (s)')

    # Set text color to white
    ax.xaxis.label.set_color(ctxt)
    ax.yaxis.label.set_color(ctxt)
    ax.title.set_color(ctxt)
    for label in itertools.chain(ax.get_xticklabels(), ax.get_yticklabels()):
        label.set_color(ctxt)

ax_mdl.set_title('10-day model runtime')
ax_cpl.set_title('10-day model wait time')

for pe in runtimes:
    for pt in runtimes[pe]['ocn']:
        ocn_handler, = ax_mdl.plot(pe, pt, 'o', markeredgewidth=1, markersize=12, color='b')

for pe in runtimes:
    for pt in runtimes[pe]['ice']:
        ice_handler, = ax_mdl.plot(pe, pt, '^', markeredgewidth=1, markersize=8, color='r')

ax.legend([ocn_handler, ice_handler], ['Ocean', 'Ice'])

for pe in runtimes:
    for pt in runtimes[pe]['ocp']:
        ax_cpl.plot(pe, pt, 'o', markeredgewidth=1, markersize=12, color='b')

for pe in runtimes:
    for pt in runtimes[pe]['icp']:
        ax_cpl.plot(pe, pt, '^', markeredgewidth=1, markersize=8, color='r')

for fmt in formats:
    plt.savefig('access_ocn_ice.{}'.format(fmt),
                facecolor='none', bbox_inches='tight')
