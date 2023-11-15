def _scan_masking_rule(shape_envs, padded_vals, shape_exprs, forward, length,
                       jaxpr, num_consts, num_carry, linear):
  out_shape = _scan_shape_rule(shape_exprs, forward, length, jaxpr,
                               num_consts, num_carry, linear)
  dynamic_length = masking.eval_dim_expr(shape_envs.logical, length)
  masked_jaxpr = _masked_scan_jaxpr(jaxpr, num_consts, num_carry)
  consts, init, xs = split_list(padded_vals, [num_consts, num_carry])
  max_length, = {x.shape[0] for x in xs}
  const_linear, init_linear, xs_linear = split_list(linear, [num_consts, num_carry])
  out_vals = scan_p.bind(
      *itertools.chain([dynamic_length] + consts, [0], init, xs),
      forward=forward, length=max_length, jaxpr=masked_jaxpr,
      num_consts=1 + num_consts, num_carry=1 + num_carry,
      linear=tuple([False] + const_linear + [False] + init_linear + xs_linear))
  return out_vals[1:], out_shape