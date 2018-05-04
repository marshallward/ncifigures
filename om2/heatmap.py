import cubex
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

fig, ax = plt.subplots()

im = ax.imshow(t, interpolation='nearest', origin='lower', cmap='viridis')

divider = make_axes_locatable(ax)
cax = divider.append_axes('right', size='5%', pad=0.05)

cbar = ax.figure.colorbar(im, ax=ax, cax=cax)
cbar.ax.set_ylabel('Time (s)', rotation=-90, va='bottom')

ax.set_xticks(4 + np.arange(0, nx, 5))
ax.set_xticklabels(5 + np.arange(0, nx, 5))

ax.set_yticks(4 + np.arange(0, ny, 5))
ax.set_yticklabels(5 + np.arange(0, ny, 5))

ax.set_title('EVP 10-day runtime')
fig.tight_layout()

plt.show()
