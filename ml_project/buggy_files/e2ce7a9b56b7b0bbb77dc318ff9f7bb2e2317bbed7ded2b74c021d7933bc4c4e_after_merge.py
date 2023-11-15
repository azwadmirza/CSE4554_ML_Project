def inv(a):
  if jnp.ndim(a) < 2 or a.shape[-1] != a.shape[-2]:
    raise ValueError(
      f"Argument to inv must have shape [..., n, n], got {a.shape}.")
  return solve(
    a, lax.broadcast(jnp.eye(a.shape[-1], dtype=lax.dtype(a)), a.shape[:-2]))