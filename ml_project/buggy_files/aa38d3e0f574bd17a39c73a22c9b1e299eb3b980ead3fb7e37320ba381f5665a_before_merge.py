def batch(fun, in_vals, in_dims, out_dim_dests):
  size, = {x.shape[d] for x, d in zip(in_vals, in_dims) if d is not not_mapped}
  out_vals, out_dims = batch_fun(fun, in_vals, in_dims)
  return map(partial(matchaxis, size), out_dims, out_dim_dests(), out_vals)