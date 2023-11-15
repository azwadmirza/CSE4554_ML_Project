def partial_eval(f, trace, pvs):
  f = trace_to_subjaxpr(f, trace.master)
  return partial_eval_wrapper(f, tuple(pvs))