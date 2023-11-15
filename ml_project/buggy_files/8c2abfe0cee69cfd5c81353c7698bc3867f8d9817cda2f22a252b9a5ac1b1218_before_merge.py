def cholesky_jvp_rule(primals, tangents):
  x, = primals
  sigma_dot, = tangents
  L = cholesky_p.bind(x)

  # Forward-mode rule from https://arxiv.org/pdf/1602.07527.pdf
  sigma_dot = (sigma_dot + _T(sigma_dot)) / 2
  phi = lambda X: np.tril(X) / (1 + np.eye(x.shape[-1]))
  tmp = triangular_solve(L, sigma_dot,
                         left_side=False, transpose_a=True, lower=True)
  L_dot = lax.dot(L, phi(triangular_solve(
      L, tmp, left_side=True, transpose_a=False, lower=True)))
  return L, L_dot