def batch(fun, in_vals, in_dims, out_dim_dests):
  # executes a batched version of `fun` following out_dim_dests
  batched_fun = batch_fun(fun, in_dims, out_dim_dests)
  return batched_fun.call_wrapped(*in_vals)