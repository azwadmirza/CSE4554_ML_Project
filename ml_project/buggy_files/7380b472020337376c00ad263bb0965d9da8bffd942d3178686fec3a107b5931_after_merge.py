def batch_fun(fun, in_dims, out_dim_dests):
  # transformation version of batch, which doesn't call the function
  fun, out_dims = batch_subtrace(fun)
  return _batch_fun(fun, in_dims, out_dims, out_dim_dests)