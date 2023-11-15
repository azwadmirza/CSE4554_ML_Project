def while_loop(cond_fun, body_fun, init_val):
  """Call `body_fun` repeatedly in a loop while `cond_fun` is True.

  Arguments:
    cond_fun: pure function of type `T -> Bool`.
    body_fun: pure function of type `T -> T`.
    init_val: value of type `T`, a type that can be a scalar, array, or any
      (nested) Python tuple/list/dict thereof.

  Returns:
    The output from the final iteration of body_fun, of type `T`.

  The semantics of `while_loop` are given by this Python implementation::

    def while_loop(cond_fun, body_fun, init_val):
      val = init_val
      while cond_fun(val):
        val = body_fun(val)
      return val

  Unlike that pure Python version, `while_loop` is a JAX primitive and is
  lowered to a single XLA While HLO. That makes it useful for reducing
  compilation times for jit-compiled functions, since native Python loop
  constructs in an `@jit` function are unrolled, leading to large XLA
  computations.

  Another difference from using Python-native loop constructs is that
  `while_loop` is not (yet) reverse-mode differentiable because XLA computations
  require static bounds on memory requirements.
  """
  init_val_flat, in_tree = pytree_to_jaxtupletree(init_val)
  flat_body_fun, out_tree = pytree_fun_to_jaxtupletree_fun(lu.wrap_init(body_fun), (in_tree,))
  flat_cond_fun, _ = pytree_fun_to_jaxtupletree_fun(lu.wrap_init(cond_fun), (in_tree,))

  carry_pval_flat = carry_aval, _ = lax._abstractify(init_val_flat)
  cond_jaxpr, cond_pval_out, cond_consts = pe.trace_to_jaxpr(flat_cond_fun, (carry_pval_flat,))
  body_jaxpr, body_pval_out, body_consts = pe.trace_to_jaxpr(flat_body_fun, (carry_pval_flat,), instantiate=True)
  carry_aval_out, _ = body_pval_out
  assert isinstance(carry_aval_out, core.AbstractValue)
  assert carry_aval == core.lattice_join(carry_aval, carry_aval_out)

  cond_pv, cond_const = cond_pval_out
  if cond_pv is None:
    # cond_fun evaluates to a constant, so don't need to generate a while_loop
    if cond_const:
      raise ValueError("infinite loop with no effects")
    else:
      return init_val
  else:
    assert isinstance(cond_pv, core.AbstractValue)
    if (not isinstance(cond_pv, ShapedArray) or cond_pv.shape
        or cond_pv.dtype != onp.bool_):
      msg = "while_loop cond_fun must return a scalar boolean, got {}."
      raise TypeError(msg.format(cond_pv))

  # We don't want to promote literal constants as loop arguments; there are
  # sometimes many of them. We pass tracers as loop arguments, but leave
  # nontracers as constants. We also sort the constants so the nontracers are
  # first.
  def split_tracers_and_nontracers(jaxpr, consts):
    tracer = []
    nontracer = []
    for x in zip(jaxpr.constvars, consts):
      # TODO(phawkins): We avoid treating DeviceArrays as constant literals so
      # we don't copy large arrays back to the host. We probably should relax
      # this and either always copy small constants, or opportunistically use
      # DeviceArray values for which we already know npy_value.
      not_literal_const = isinstance(x[1], (core.Tracer, xla.DeviceArray))
      (tracer if not_literal_const else nontracer).append(x)
    tracer_vars, tracer_consts = unzip2(tracer)
    nontracer_vars, nontracer_consts = unzip2(nontracer)
    return nontracer_vars + tracer_vars, nontracer_consts, tracer_consts

  cond_split = split_tracers_and_nontracers(cond_jaxpr, cond_consts)
  cond_jaxpr.constvars, cond_nontracer_consts, cond_tracer_consts = cond_split
  body_split = split_tracers_and_nontracers(body_jaxpr, body_consts)
  body_jaxpr.constvars, body_nontracer_consts, body_tracer_consts = body_split

  if out_tree() != in_tree:
    raise TypeError("body_fun input and output must have identical structure")
  out_flat = while_p.bind(
      init_val_flat,
      core.pack(cond_tracer_consts), core.pack(body_tracer_consts),
      cond_consts=lax._OpaqueParam(cond_nontracer_consts),
      body_consts=lax._OpaqueParam(body_nontracer_consts),
      aval_out=carry_aval_out, cond_jaxpr=cond_jaxpr, body_jaxpr=body_jaxpr)
  return build_tree(out_tree(), out_flat)