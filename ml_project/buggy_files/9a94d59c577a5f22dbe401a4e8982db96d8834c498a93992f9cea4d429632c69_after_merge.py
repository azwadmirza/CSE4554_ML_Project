def cholesky(x, symmetrize_input=True):
  if symmetrize_input:
    x = symmetrize(x)
  return cholesky_p.bind(x)