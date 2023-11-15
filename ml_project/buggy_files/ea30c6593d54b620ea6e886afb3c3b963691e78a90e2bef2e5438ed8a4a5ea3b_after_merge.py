def xla_callable(fun, *abstract_args):
  pvals = [pe.PartialVal((aval, core.unit)) for aval in abstract_args]
  with core.new_master(pe.JaxprTrace, True) as master:
    jaxpr, (pval, consts, env) = pe.trace_to_subjaxpr(fun, master, False).call_wrapped(pvals)
    assert not env  # no subtraces here (though cond might eventually need them)
    compiled, result_shape = compile_jaxpr(jaxpr, consts, *abstract_args)
    del master, consts, jaxpr, env
  handle_result = result_handler(result_shape)
  return partial(execute_compiled, compiled, pval, handle_result)