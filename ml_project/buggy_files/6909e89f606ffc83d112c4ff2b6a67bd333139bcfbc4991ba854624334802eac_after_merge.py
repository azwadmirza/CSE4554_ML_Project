def _scan_transpose(cts, *args, forward, length, num_consts, num_carry, jaxpr, linear):
  # we've only implemented transposing scans with specific lin/nonlin patterns
  consts_lin, init_lin, xs_lin = split_list(linear, [num_consts, num_carry])
  num_ires = len(consts_lin) - sum(consts_lin)
  num_eres = len(xs_lin) - sum(xs_lin)
  if consts_lin != [False] * num_ires + [True] * (len(consts_lin) - num_ires):
    raise NotImplementedError
  if xs_lin != [True] * (len(xs_lin) - num_eres) + [False] * num_eres:
    raise NotImplementedError
  if not all(init_lin):
    pass  # TODO(mattjj): error check https://github.com/google/jax/issues/1963

  consts, _, xs = split_list(args, [num_consts, num_carry])
  ires, _ = split_list(consts, [num_ires])
  _, eres = split_list(xs, [sum(xs_lin)])
  assert not any(r is ad.undefined_primal for r in ires)
  assert not any(r is ad.undefined_primal for r in eres)

  carry_avals, y_avals = split_list(jaxpr.out_avals, [num_carry])
  ys_avals = _map(partial(_promote_aval_rank, length), y_avals)
  ct_carry, ct_ys = split_list(cts, [num_carry])
  ct_carry = _map(ad.instantiate_zeros_aval, carry_avals, ct_carry)
  ct_ys = _map(ad.instantiate_zeros_aval, ys_avals, ct_ys)
  ct_consts = _map(ad_util.zeros_like_aval, jaxpr.in_avals[num_ires:num_consts])

  #       jaxpr :: [ires, T d] -> [T c] -> [T a, eres] -> ([T c], [T b])
  # jaxpr_trans :: [ires] -> [CT d, CT c] -> [CT b, eres] -> ([CT d, CT c], [CT a])
  jaxpr_trans = _transpose_scan_jaxpr(
      num_ires, num_consts - num_ires, num_eres, jaxpr)
  linear_trans = ([False] * num_ires +
                  [True] * (len(ct_consts) + len(ct_carry) + len(ct_ys)) +
                  [False] * num_eres)

  outs = scan_p.bind(
      *(ires + ct_consts + ct_carry + ct_ys + eres), forward=not forward,
      length=length, jaxpr=jaxpr_trans, num_consts=num_ires,
      num_carry=num_consts-num_ires+num_carry, linear=tuple(linear_trans))
  ct_consts, ct_init, ct_xs = split_list(outs, [num_consts - num_ires, num_carry])
  return [None] * num_ires + ct_consts + ct_init + ct_xs + [None] * num_eres