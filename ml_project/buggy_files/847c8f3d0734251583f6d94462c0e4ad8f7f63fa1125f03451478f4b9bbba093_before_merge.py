def _while_loop_translation_rule(c, axis_env, name_stack, avals, backend, *args,
                                 cond_jaxpr, body_jaxpr, cond_nconsts, body_nconsts):
  cond_consts, body_consts, init_vals = split_list(args, [cond_nconsts, body_nconsts])
  batched = bool(cond_jaxpr.out_avals[0].shape)

  # Since jaxprs don't have tuples and have multiple return values, but we need
  # the HLO While loop to take a single tuple input and output a single boolean
  # (for the cond computation) or a single tuple output (for the body
  # computation), we build XLA computations that handle the tuple munging before
  # generating a Call into the computations formed from the jaxprs.

  init_carry = xops.Tuple(c, cond_consts + body_consts + init_vals)

  cond_c = xb.make_computation_builder("cond_computation")
  cond_carry = xb.parameter(cond_c, 0, c.get_shape(init_carry))
  cond_carry_elts = [xops.GetTupleElement(cond_carry, i) for i in range(len(args))]
  x, _, z = split_list(cond_carry_elts, [cond_nconsts, body_nconsts])
  pred, = xla.jaxpr_subcomp(cond_c, cond_jaxpr.jaxpr, backend, axis_env,
                            _map(partial(xb.constant, cond_c),
                                 cond_jaxpr.literals),
                            extend_name_stack(name_stack, 'cond'), *(x + z))
  if batched:
    scalar = ShapedArray((), onp.bool_)
    or_ = xla.primitive_subcomputation(lax.or_p, scalar, scalar)
    pred = xops.Reduce(cond_c, [pred], [xb.constant(cond_c, onp.array(False))], or_,
                         list(range(cond_jaxpr.out_avals[0].ndim)))

  body_c = xb.make_computation_builder("body_computation")
  body_carry = xb.parameter(body_c, 0, c.get_shape(init_carry))
  body_carry_elts = [xops.GetTupleElement(body_carry, i) for i in range(len(args))]
  x, y, z = split_list(body_carry_elts, [cond_nconsts, body_nconsts])
  new_z = xla.jaxpr_subcomp(body_c, body_jaxpr.jaxpr, backend, axis_env,
                            _map(partial(xb.constant, body_c), body_jaxpr.literals),
                            extend_name_stack(name_stack, 'body'), *(y + z))
  if batched:
    body_pred, = xla.jaxpr_subcomp(body_c, cond_jaxpr.jaxpr, backend, axis_env,
                                   _map(partial(xb.constant, body_c), cond_jaxpr.literals),
                                   extend_name_stack(name_stack, 'body_pred'), *(x + z))
    new_z = _map(partial(_pred_bcast_select, body_c, body_pred), new_z, z)
    assert _map(body_c.get_shape, new_z) == _map(body_c.get_shape, z) # no broadcast
  new_carry = xops.Tuple(body_c, list(itertools.chain(x, y, new_z)))

  ans = xops.While(cond_c.build(pred), body_c.build(new_carry), init_carry)
  ans_elts = [xops.GetTupleElement(ans, i) for i in range(len(args))]
  _,  _, z = split_list(ans_elts, [cond_nconsts, body_nconsts])
  return xops.Tuple(c, z)