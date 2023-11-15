def parallel_callable(fun, axis_name, axis_size, *avals):
  pvals = [PartialVal((aval, core.unit)) for aval in avals]
  with core.new_master(JaxprTrace, True) as master:
    jaxpr, (pval, consts, env) = trace_to_subjaxpr(fun, master, False).call_wrapped(pvals)
    assert not env
    out = compile_replicated(jaxpr, axis_name, axis_size, consts, *avals)
    compiled, nrep, result_shape = out
    del master, consts, jaxpr, env
  handle_arg = partial(shard_arg, compiled._device_ordinals)
  handle_result = xla.result_handler(result_shape)
  return partial(execute_replicated, compiled, pval, axis_size, nrep,
                 handle_arg, handle_result)