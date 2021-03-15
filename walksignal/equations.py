import numpy as np
import scipy.special as sp

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd2d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (2 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    bessel = internal_multiplier * sp.kv(0, exp_mult_1 * x_range)
    first_component = internal_multiplier * np.multiply(x_range, bessel)
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y

# Equation 12 in A Random Walk Model of Wave Propagation
def gplt_rwm_fpd3d(obs_dens, absorption, x_range):
    external_multiplier = obs_dens * absorption / (4 * np.pi)
    internal_multiplier = (1 - absorption) * obs_dens
    exp_mult_1 = np.sqrt(1 - np.square(1 - absorption)) * obs_dens
    exp_mult_2 = -1 * (1 - np.square(1 - absorption)) * obs_dens
    first_component = internal_multiplier * np.multiply(x_range, np.exp(-1 * exp_mult_1 * x_range))
    second_component = np.exp(exp_mult_2 * x_range)
    g_r = external_multiplier * np.multiply(np.add(first_component, second_component), x_range)
    rwm_y = 10 * np.log10(g_r / (absorption * obs_dens)) + 30

    return rwm_y
