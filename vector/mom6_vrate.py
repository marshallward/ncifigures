from cubex.cube import Cube
import numpy as np

dp = Cube()
dp.parse('mom6_dp.cubex')
dp.read_data('PAPI_DP_OPS')

vec = Cube()
vec.parse('mom6_vec.cubex')
vec.read_data('PAPI_VEC_DP')

regions = [
    'MAIN__',
    'ocean_model_mod.update_ocean_model_',
        'mom_dynamics_split_rk2.step_mom_dyn_split_rk2_',
            'mom_barotropic.btstep_',
            'mom_domains.do_group_pass_',
            'mom_continuity.continuity_',
            'mom_barotropic.set_dtbt_',
            'mom_pressureforce.pressureforce_',
            'mom_set_visc.set_viscous_bbl_',
        'mom_ale.ale_main_',
        'mom_diabatic_driver.diabatic_',
        'mom_mixed_layer_restrat.mixedlayer_restrat_',
        'mom_set_visc.set_viscous_bbl_',
        'mom_tracer_advect.advect_tracer_',
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
    #print(rgn, "{:.03} ({:.2e} / {:.2e})".format(vecrate.mean(), dp_sum, vec_sum))

    rname = rgn.split('.')[-1].rstrip("_")

    # HTML output
    print("<tr>")
    print("  <td>{}</td>".format(rname))
    print("  <td>{:.2e}</td>".format(dp_sum))
    #print("  <td>{:.3}</td>".format(vecrate.mean()))
    print("  <td>{:.3}</td>".format(vecrate))
    print("</tr>")
