def backward_pass(jaxpr: core.Jaxpr, consts, args, cotangents_in):
  if all(ct is zero for ct in cotangents_in):
    return [zero] * len(jaxpr.invars)

  def write_cotangent(v, ct):
    # assert v not in primal_env
    if ct is not None and type(v) is not Literal:
      ct_env[v] = add_tangents(ct_env[v], ct) if v in ct_env else ct

  def read_cotangent(v):
    return ct_env.get(v, zero)

  def read_primal(v):
    if type(v) is Literal:
      return v.val
    else:
      return primal_env.get(v, undefined_primal)

  def write_primal(v, val):
    if val is not undefined_primal:
      primal_env[v] = val

  primal_env = {}
  write_primal(core.unitvar, core.unit)
  map(write_primal, jaxpr.constvars, consts)
  map(write_primal, jaxpr.invars, args)

  def is_linear(var):
    if type(var) is Literal:
      return False
    else:
      return primal_env.get(var, undefined_primal) is undefined_primal

  linear_eqns = []
  for eqn in jaxpr.eqns:
    if not eqn.primitive.call_primitive:
      if any(is_linear(v) for v in eqn.invars):
        linear_eqns.append(eqn)
      else:
        in_vals = map(read_primal, eqn.invars)
        ans = eqn.primitive.bind(*in_vals, **eqn.params)
        if eqn.primitive.multiple_results:
          map(write_primal, eqn.outvars, ans)
        else:
          write_primal(eqn.outvars[0], ans)
    else:
      call_jaxpr, params = core.extract_call_jaxpr(eqn.primitive, eqn.params)
      if any(is_linear(v) for v in eqn.invars):
        linear_eqns.append(eqn)
      if any(not is_linear(v) for v in eqn.invars):
        ans = _eval_subjaxpr_primals(eqn.primitive, call_jaxpr,
                                     map(read_primal, eqn.invars), params)
        map(write_primal, eqn.outvars, ans)

  ct_env = {}
  map(write_cotangent, jaxpr.outvars, cotangents_in)
  for eqn in linear_eqns[::-1]:
    invals = map(read_primal, eqn.invars)
    if eqn.primitive.multiple_results:
      cts_in = map(read_cotangent, eqn.outvars)
    else:
      cts_in, = map(read_cotangent, eqn.outvars)
    if eqn.primitive.call_primitive:
      call_jaxpr, params = core.extract_call_jaxpr(eqn.primitive, eqn.params)
      cts_out = get_primitive_transpose(eqn.primitive)(
          params, call_jaxpr, invals, cts_in)
    else:
      cts_out = get_primitive_transpose(eqn.primitive)(cts_in, *invals, **eqn.params)
    cts_out = [zero] * len(eqn.invars) if cts_out is zero else cts_out
    map(write_cotangent, eqn.invars, cts_out)

  cotangents_out = map(read_cotangent, jaxpr.invars)
  return cotangents_out