def _rewrite_eqn(eqn: core.JaxprEqn, eqns: List[core.JaxprEqn],
                 input_token_var: core.Var, output_token_var: core.Var,
                 mk_new_var: Callable[[core.AbstractValue], core.Var]):
  """Rewrite an `eqn` and append equations to `eqns`.

  Assume that the current token is in `input_token_var` and the resulting
  token must end in `output_token_var`.
  """
  if eqn.primitive is id_tap_p:
    assert "has_token_" not in eqn.params
    eqns.append(
        core.new_jaxpr_eqn(eqn.invars + [input_token_var],
                           eqn.outvars + [output_token_var], eqn.primitive,
                           dict(eqn.params, has_token_=True),
                           eqn.source_info))
  elif eqn.primitive is lax.while_p:
    cond_jaxpr, _, body_jaxpr, _ = util.split_dict(
        eqn.params,
        ["cond_jaxpr", "cond_nconsts", "body_jaxpr", "body_nconsts"])
    if xla.jaxpr_uses_outfeed(cond_jaxpr.jaxpr):
      _rewrite_while_outfeed_cond(eqn, eqns, input_token_var, output_token_var,
                                  mk_new_var)
      return

    eqns.append(
        core.new_jaxpr_eqn(
            eqn.invars + [input_token_var], eqn.outvars + [output_token_var],
            eqn.primitive,
            dict(
                eqn.params,
                body_jaxpr=_rewrite_typed_jaxpr(body_jaxpr, True, True),
                cond_jaxpr=_rewrite_typed_jaxpr(cond_jaxpr, True,
                                                False)), eqn.source_info))
  elif eqn.primitive is lax.cond_p:
    branches, linear = util.split_dict(eqn.params, ["branches", "linear"])
    index, *operands = eqn.invars
    new_invars = [index, *operands, input_token_var]
    eqns.append(
        core.new_jaxpr_eqn(
            new_invars, eqn.outvars + [output_token_var], eqn.primitive,
            dict(
                eqn.params,
                branches=tuple(
                    _rewrite_typed_jaxpr(jaxpr, True, True)
                    for jaxpr in branches),
                linear=(*linear, False)), eqn.source_info))
  elif eqn.primitive is lax.scan_p:
    num_consts, num_carry, carry_jaxpr, linear, _, _, _ = util.split_dict(
        eqn.params,
        ["num_consts", "num_carry", "jaxpr", "linear", "reverse", "length",
         "unroll"])
    # We add the token right at the end of carry
    nr_const_and_carry = num_consts + num_carry
    new_invars = eqn.invars[0:nr_const_and_carry] + [
        input_token_var
    ] + eqn.invars[nr_const_and_carry:]
    new_jaxpr = _rewrite_typed_jaxpr(carry_jaxpr, True, True)
    # The rewrite has put the token at end, it has to be at end of carry
    new_jaxpr_invars = new_jaxpr.jaxpr.invars
    new_jaxpr_invars = (
        new_jaxpr_invars[0:nr_const_and_carry] + [new_jaxpr_invars[-1]] +
        new_jaxpr_invars[nr_const_and_carry:-1])
    new_jaxpr.jaxpr.invars = new_jaxpr_invars
    new_jaxpr.in_avals = [v.aval for v in new_jaxpr_invars]

    new_jaxpr_outvars = new_jaxpr.jaxpr.outvars
    new_jaxpr_outvars = (
        new_jaxpr_outvars[0:num_carry] + [new_jaxpr_outvars[-1]] +
        new_jaxpr_outvars[num_carry:-1])
    new_jaxpr.jaxpr.outvars = new_jaxpr_outvars
    new_jaxpr.out_avals = [v.aval for v in new_jaxpr_outvars]
    eqns.append(
        core.new_jaxpr_eqn(
            new_invars,
            # Output token is at the end of carry result
            eqn.outvars[0:num_carry] + [output_token_var] +
            eqn.outvars[num_carry:],
            eqn.primitive,
            dict(
                eqn.params,
                jaxpr=new_jaxpr,
                num_carry=num_carry + 1,
                linear=linear + (False,)),
            eqn.source_info))
  elif eqn.primitive is xla.xla_call_p:
    call_jaxpr = cast(core.Jaxpr, eqn.params["call_jaxpr"])
    eqns.append(
        core.new_jaxpr_eqn(
            eqn.invars + [input_token_var], eqn.outvars + [output_token_var],
            eqn.primitive,
            dict(
                eqn.params,
                call_jaxpr=_rewrite_jaxpr(call_jaxpr, True,
                                          True),
                donated_invars=eqn.params["donated_invars"] + (False,)
            ),
          eqn.source_info))
  elif eqn.primitive is custom_derivatives.custom_jvp_call_jaxpr_p:
    fun_jaxpr = eqn.params["fun_jaxpr"]
    new_invars = [*eqn.invars, input_token_var]
    def unreachable_thunk():
      assert False, "Should not be reached"
    eqns.append(
        core.new_jaxpr_eqn(
            new_invars, eqn.outvars + [output_token_var], eqn.primitive,
            dict(
                eqn.params,
                fun_jaxpr=_rewrite_typed_jaxpr(fun_jaxpr, True, True),
                jvp_jaxpr_thunk=unreachable_thunk
            ),
            eqn.source_info))
  elif eqn.primitive is custom_derivatives.custom_vjp_call_jaxpr_p:
    fun_jaxpr = eqn.params["fun_jaxpr"]
    new_invars = [*eqn.invars, input_token_var]
    def unreachable_thunk():
      assert False, "Should not be reached"
    eqns.append(
        core.new_jaxpr_eqn(
            new_invars, eqn.outvars + [output_token_var], eqn.primitive,
            dict(
                eqn.params,
                fun_jaxpr=_rewrite_typed_jaxpr(fun_jaxpr, True, True),
                fwd_jaxpr_thunk=unreachable_thunk,
                # The following are illegal values for the parameters, they
                # should not be needed because this rewrite is just before
                # compilation to XLA, which does not use those parameters.
                bwd="illegal param",
                out_trees="illegal param"
            ),
            eqn.source_info))
  else:
    raise NotImplementedError(f"outfeed rewrite {eqn.primitive}")