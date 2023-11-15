def trace_to_jaxpr(fun, pvals, **kwargs):
  """Traces a function, given abstract inputs, to a jaxpr."""
  instantiate = kwargs.pop('instantiate', False)
  with new_master(JaxprTrace) as master:
    fun = trace_to_subjaxpr(fun, master, instantiate)
    jaxpr, (out_pval, consts, env) = fun.call_wrapped(pvals)
    assert not env
    del master

  return jaxpr, out_pval, consts