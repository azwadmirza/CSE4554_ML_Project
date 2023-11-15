def batch_fun(fun, in_vals, in_dims):
  with new_master(BatchTrace) as master:
    fun, out_dims = batch_subtrace(fun, master, in_dims)
    out_vals = fun.call_wrapped(*in_vals)
    del master
  return out_vals, out_dims()