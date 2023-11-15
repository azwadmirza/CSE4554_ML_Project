def _jvp_slogdet(g, ans, x):
  jvp_sign = np.zeros(x.shape[:-2])
  jvp_logdet = np.trace(solve(x, g), axis1=-1, axis2=-2)
  return jvp_sign, jvp_logdet