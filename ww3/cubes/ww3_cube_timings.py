#!/usr/bin/env python

from collections import defaultdict
import os
import sys

from cubex.cube import Cube
import numpy as np
import yaml

def main():

    timings = {}

    # Skip empty directories
    cube_files = [f for f in os.listdir() if f.endswith('.cubex')]

    for fname in cube_files:
        tag = fname.rsplit('.', 1)[0]
        timings[tag] = {}

        npes = int([t.rstrip('pe') for t in tag.split('_')
                    if t[-2:] == 'pe'][0])
        timings[tag]['npes'] = npes

        runtimes = parse_cube(fname)
        timings[tag]['runtimes'] = runtimes

        timings_out_path = 'ww3_timings.yaml'
        with open(timings_out_path, 'w') as timings_out:
            yaml.dump(dict(timings), timings_out, default_flow_style=False)


def parse_cube(cube_path):
    cube = Cube()
    cube.parse(cube_path)
    cube.read_data('time')

    runtimes = {}

    f_regions = [
        'w3initmd.w3init_',
        'w3iorsmd.w3iors_',
        'w3wavemd.w3wave_',
        'w3wavemd.w3gath_',
        'w3iosfmd.w3cprt_',
        'w3pro3md.w3xyp3_',
        'w3srcemd.w3srce_',
        'w3pro3md.w3ktp3_',
        'w3wavemd.w3scat_',
        'w3iogomd.w3outg_',
    ]

    for fname in f_regions:
        cnodes = cube.regions[fname].cnodes
        if len(cnodes) > 1:
            cn_idx = None
            for idx, cn in enumerate(cnodes):
                print(cn.region.name, idx)
                print(cn.parent)
                if cn.parent.region.name == 'w3wavemd.w3wave_':
                    cn_idx = idx
                    break
            assert cn_idx
        else:
            cn_idx = 0

        vals = cnodes[cn_idx].metrics['time']

        rt = {}
        rt['min'] = min(vals)
        rt['max'] = max(vals)
        rt['mean'] = float(np.array(vals).mean())
        rt['std'] = float(np.array(vals).std())

        fkey = fname.split('.')[-1].rstrip('_')
        runtimes[fkey] = rt

    return runtimes


if __name__ == '__main__':
    main()
