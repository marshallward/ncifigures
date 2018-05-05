import cubex
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

nx, ny = 40, 30
ncpus = nx * ny
region_name = 'ice_dyn_evp.evp_'
#region_name = 'ice_step_mod.step_dynamics_'

cube = cubex.open('01base.cubex')
cube.read_data('time')

step_dyn = cube.regions[region_name].cnodes[0]
t = np.array(step_dyn.metrics['time'][1:(ncpus + 1)]).reshape(ny, nx)

t_max = (np.max(t) // 200 + 1) * 200

for color, fmt in zip(('k', 'w'), ('pdf', 'svg')):
    plt.rc_context({
        'text.color': color,
        'axes.labelcolor': color,
        'xtick.color': color,
        'ytick.color': color,
    })

    fig, ax = plt.subplots()

    im = ax.imshow(t, vmin=0., vmax=t_max,
                   interpolation='nearest', origin='lower', cmap='viridis')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)

    cbar = ax.figure.colorbar(im, ax=ax, cax=cax)
    cbar.ax.set_ylabel('Time (s)', rotation=-90, va='bottom')
    cbar.set_ticks(np.linspace(0., t_max, 9))

    ax.set_xticks(4 + np.arange(0, nx, 5))
    ax.set_xticklabels(5 + np.arange(0, nx, 5))

    ax.set_yticks(4 + np.arange(0, ny, 5))
    ax.set_yticklabels(5 + np.arange(0, ny, 5))

    ax.set_title('CICE: EVP 10-day runtime')
    fig.tight_layout()

    fig.savefig('evp_heatmap_{}.{}'.format(color, fmt), facecolor='none')
