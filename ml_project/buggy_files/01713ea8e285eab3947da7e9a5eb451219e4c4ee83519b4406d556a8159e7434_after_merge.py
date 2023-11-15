def _jvp_slogdet(g, ans, x):
  if np.issubdtype(np._dtype(x), np.complexfloating):
    raise NotImplementedError  # TODO(pfau): make this work for complex types
  jvp_logdet = np.trace(solve(x, g), axis1=-1, axis2=-2)
  return ad_util.zero, jvp_logdet