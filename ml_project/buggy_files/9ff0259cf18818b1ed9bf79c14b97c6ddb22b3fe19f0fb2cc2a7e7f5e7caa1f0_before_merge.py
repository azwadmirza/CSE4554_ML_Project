def choice(key, a, shape=(), replace=True, p=None):
  """Generates a random sample from a given 1-D array.

  Args:
    key: a PRNGKey used as the random key.
    a : 1D array or int. If an ndarray, a random sample is generated from
      its elements. If an int, the random sample is generated as if a were
      arange(a).
    shape : tuple of ints, optional. Output shape.  If the given shape is,
      e.g., ``(m, n)``, then ``m * n`` samples are drawn.  Default is (),
      in which case a single value is returned.
    replace : boolean.  Whether the sample is with or without replacement.
      default is True.
    p : 1-D array-like, The probabilities associated with each entry in a.
      If not given the sample assumes a uniform distribution over all
      entries in a.

  Returns:
    An array of shape `shape` containing samples from `a`.
  """
  a = jnp.asarray(a)
  if a.ndim not in [0, 1]:
    raise ValueError("a must be an integer or 1-dimensional")
  n_inputs = int(a) if a.ndim == 0 else len(a)
  n_draws = prod(shape)
  if n_draws == 0:
    return jnp.zeros(shape, dtype=a.dtype)
  if n_inputs <= 0:
    raise ValueError("a must be greater than 0 unless no samples are taken")
  if not replace and n_draws > n_inputs:
    raise ValueError("Cannot take a larger sample than population when 'replace=False'")

  if p is None:
    if replace:
      ind = randint(key, shape, 0, n_inputs)
      result = ind if a.ndim == 0 else a[ind]
    else:
      result = permutation(key, a)[:n_draws]
  else:
    p = jnp.asarray(p)
    if p.shape != (n_inputs,):
      raise ValueError("p must be None or match the shape of a")
    if replace:
      p_cuml = jnp.cumsum(p)
      r = p_cuml[-1] * (1 - uniform(key, shape))
      ind = jnp.searchsorted(p_cuml, r)
      result = ind if a.ndim == 0 else a[ind]
    else:
      # Gumbel top-k trick: https://timvieira.github.io/blog/post/2019/09/16/algorithms-for-sampling-without-replacement/
      g = -gumbel(key, (n_inputs,)) - jnp.log(p)
      ind = jnp.argsort(g)[:n_draws]
      result = ind if a.ndim == 0 else a[ind]
  return result.reshape(shape)