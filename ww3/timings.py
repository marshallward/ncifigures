#!/usr/bin/env python

import os

import numpy as np

from cubex.cube import Cube

#fn_name = 'w3initmd.w3init_'
#fn_name = 'w3wavemd.w3wave_'
#fn_name = 'w3wavemd.w3gath_'
#fn_name = 'w3iorsmd.w3iors_'
#fn_name = 'w3pro3md.w3xyp3_'
#fn_name = 'w3srcemd.w3srce_'
#fn_name = 'w3iosfmd.w3cprt_'
fn_name = 'w3wavemd.w3scat_'

cube_fpaths = [f for f in os.listdir(os.curdir) if f.startswith('ww3')]

results = {}

for fpath in cube_fpaths:
    pe = int(fpath[4:].strip('pe.cubex'))

    print('parsing {}'.format(fpath))

    cube = Cube()
    cube.parse(fpath)

    m_time = None
    for metric in cube.metrics:
        if metric.name == 'time':
            m_time = metric
            break
    assert m_time
    cube.read_data(m_time)

    # Get the function index
    ridx = None
    for idx, rnode in enumerate(cube.regions):

        if rnode.name == fn_name:
            ridx = idx
            break
        
    assert ridx

    cnode = None
    for cn in cube.cindex:
        if cn.region_id == ridx:
            cnode = cn
    assert cnode

    timing = np.mean(cnode.metrics['time'][:])

    print(pe)
    results[pe] = timing

for pe in sorted(results.keys()):
    print(pe, results[pe])
