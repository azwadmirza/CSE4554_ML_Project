def _eval_primals(jaxpr, args):
  primal_env = {}

  def read_primal(v):
    if type(v) is Literal:
      return v.val
    else:
      return primal_env.get(v, undefined_primal)

  def write_primal(v, val):
    if val is not undefined_primal:
      primal_env[v] = val

  def is_linear(var):
    if type(var) is Literal:
      return False
    else:
      return primal_env.get(var, undefined_primal) is undefined_primal

  write_primal(core.unitvar, core.unit)
  assert not jaxpr.constvars
  map(write_primal, jaxpr.invars, args)
  for eqn in jaxpr.eqns:
    if not eqn.primitive.call_primitive:
      if not any(is_linear(v) for v in eqn.invars):
        in_vals = map(read_primal, eqn.invars)
        ans = eqn.primitive.bind(*in_vals, **eqn.params)
        if eqn.primitive.multiple_results:
          map(write_primal, eqn.outvars, ans)
        else:
          write_primal(eqn.outvars[0], ans)
    else:
      call_jaxpr = eqn.params["call_jaxpr"]
      if (eqn.primitive is pe.remat_call_p or
          not any(is_linear(v) for v in eqn.invars)):
        ans = _eval_subjaxpr_primals(
            eqn.primitive, call_jaxpr,
            map(read_primal, eqn.invars), eqn.params)
        map(write_primal, eqn.outvars, ans)
  return map(read_primal, jaxpr.outvars)