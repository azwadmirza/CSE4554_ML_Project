def primitive_computation(prim, axis_env, backend, tuple_args, *avals, **params):
  c = xb.make_computation_builder(f"primitive_computation_{prim.name}")
  c.set_op_metadata(xc.OpMetadata(
      op_type=prim.name,
      op_name=str(pp_eqn_compact(prim.name, params))))
  platform = xb.get_backend(backend).platform
  xla_args, _ = _xla_callable_args(c, avals, tuple_args)
  # return val always set as a side-effect on c
  if prim in backend_specific_translations[platform]:
    rule = backend_specific_translations[platform][prim]
    ans = rule(c, *xla_args, **params)
  elif prim in translations:
    rule = translations[prim]
    ans = rule(c, *xla_args, **params)
  elif prim in initial_style_translations:
    rule = initial_style_translations[prim]
    ans = rule(c, axis_env, extend_name_stack(prim.name), avals, backend,
         *xla_args, **params)
  else:
    raise NotImplementedError(f"XLA translation rule for {prim} not found")
  assert isinstance(ans, xe.XlaOp)
  c.clear_op_metadata()
  try:
    return c.build(ans)
  except RuntimeError as e:
    msg = (" ".join(map(str, e.args)) + "\n"
           "This is a bug in JAX's shape-checking rules; please report it!\n"
           "https://github.com/google/jax/issues\n")
    raise RuntimeError(msg) from e