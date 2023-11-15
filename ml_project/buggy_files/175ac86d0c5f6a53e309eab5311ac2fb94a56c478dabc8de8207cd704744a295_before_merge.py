def trace_to_subjaxpr(master, pvals):
  assert all([isinstance(pv, PartialVal) for pv in pvals]), pvals
  trace = JaxprTrace(master, core.cur_sublevel())
  in_tracers = map(trace.new_arg, pvals)
  out_tracer = yield in_tracers, {}
  out_tracer = trace.full_raise(out_tracer)
  jaxpr, consts, env = tracers_to_jaxpr(in_tracers, out_tracer)
  out_pval = out_tracer.pval
  del trace, in_tracers, out_tracer
  yield jaxpr, (out_pval, consts, env)