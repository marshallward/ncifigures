from cubex.cube import Cube
import numpy as np

dp = Cube()
dp.parse('orca_dp.cubex')
dp.read_data('PAPI_DP_OPS')

vec = Cube()
vec.parse('orca_vec.cubex')
vec.read_data('PAPI_VEC_DP')

regions = [
    'step.stp_',
    'dynspg.dyn_spg_',
    'traadv.tra_adv_',
    'tradmp.tra_dmp_',
    'ldfslp.ldf_slp_',
    'sbcmod.sbc_',
    'sbcice_lim_2.sbc_ice_lim_2_',
    'limdyn_2.lim_dyn_2_',
    'limtrp_2.lim_trp_2_',
]


for rgn in regions:
    # Use cnode[0] for now
    dp_vals = dp.regions[rgn].cnodes[0].metrics['PAPI_DP_OPS']
    vec_vals = vec.regions[rgn].cnodes[0].metrics['PAPI_VEC_DP']

    dp_mean = np.array(dp_vals).mean()
    vec_mean = np.array(vec_vals).mean()
    vecrate = np.array(vec_vals) / np.array(dp_vals)
    #print(rgn, "{:.03} ({:.2e} / {:.2e})".format(vecrate.mean(), dp_mean, vec_mean))

    rname = rgn.split('.')[-1].rstrip("_")

    # HTML output
    print("<tr>")
    print("  <td>{}</td>".format(rname))
    print("  <td>{:.2e}</td>".format(dp_mean))
    print("  <td>{:.3}</td>".format(vecrate.mean()))
    print("</tr>")
