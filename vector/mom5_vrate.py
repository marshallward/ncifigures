from cubex.cube import Cube
import numpy as np

dp = Cube()
dp.parse('mom5_dp.cubex')
dp.read_data('PAPI_DP_OPS')

vec = Cube()
vec.parse('mom5_vec.cubex')
vec.read_data('PAPI_VEC_DP')

regions = [
    'MAIN__',
    'ocean_model_mod.update_ocean_model_',
    'ocean_tracer_mod.update_ocean_tracer_',
    'ocean_vert_mix_mod.vert_mix_coeff_',
    'ocean_velocity_mod.ocean_explicit_accel_a_',
    'ocean_barotropic_mod.update_ocean_barotropic_',
    'ocean_submesoscale_mod.submeso_restrat_',
    'ocean_barotropic_mod.ocean_eta_smooth_',
    'ice_model_mod.update_ice_model_slow_dn_',
]


for rgn in regions:
    # Use cnode[0] for now
    dp_vals = dp.regions[rgn].cnodes[0].metrics['PAPI_DP_OPS']
    vec_vals = vec.regions[rgn].cnodes[0].metrics['PAPI_VEC_DP']

    dp_sum = np.array(dp_vals).sum()
    vec_sum = np.array(vec_vals).sum()
    #vecrate = np.array(vec_vals) / np.array(dp_vals)
    vecrate = vec_sum / dp_sum
    #print(rgn, "{:.03} ({:.2e} / {:.2e})".format(vecrate.mean(), dp_mean, vec_mean))

    rname = rgn.split('.')[-1].rstrip("_")

    # HTML output
    print("<tr>")
    print("  <td>{}</td>".format(rname))
    print("  <td>{:.2e}</td>".format(dp_sum))
    #print("  <td>{:.3}</td>".format(vecrate.mean()))
    print("  <td>{:.3}</td>".format(vecrate))
    print("</tr>")
