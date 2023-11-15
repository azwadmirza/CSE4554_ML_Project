def trace_to_jaxpr(fun, pvals):
  """Traces a function, given abstract inputs, to a jaxpr."""
  with new_master(JaxprTrace) as master:
    fun = trace_to_subjaxpr(fun, master)
    jaxpr, (out_pval, consts, env) = fun.call_wrapped(pvals)
    assert not env
    del master

  return jaxpr, out_pval, consts