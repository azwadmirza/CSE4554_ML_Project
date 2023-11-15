def mask(fun: Callable, in_shapes, out_shape) -> Callable:
  _check_callable(fun)
  in_specs, in_shapes_tree = tree_flatten(in_shapes)
  out_specs, out_shapes_tree = tree_flatten(out_shape)

  in_specs = map(masking.parse_spec, in_specs)
  out_specs = map(masking.parse_spec, out_specs)

  unique_ids: Dict[Any, Any] = collections.defaultdict(object)
  in_specs  = map(partial(_remap_ids, unique_ids), in_specs)
  out_specs = map(partial(_remap_ids, unique_ids), out_specs)

  def wrapped_fun(args, logical_env):
    args_flat, in_tree = tree_flatten(args)
    if in_tree != in_shapes_tree: raise TypeError("pytree mismatch")
    logical_env = {unique_ids[name] : val for name, val in logical_env.items()}
    in_shapes = map(masking.finalize_spec, in_specs, map(onp.shape, args_flat))
    padded_env = _bind_shapes(in_shapes, [x.shape for x in args_flat])
    f = lu.wrap_init(fun)
    flat_fun, out_tree = flatten_fun_nokwargs(f, in_tree)
    outs, out_shapes_ = masking.mask_fun(
        flat_fun, logical_env, padded_env, args_flat, in_shapes)
    if not out_tree() == out_shapes_tree: raise TypeError("pytree mismatch")
    out_shapes = map(masking.finalize_spec, out_specs, map(onp.shape, outs))
    if not out_shapes == list(out_shapes_):
      raise masking.ShapeError
    if not all(onp.shape(out) == eval_polymorphic_shape(shape, padded_env)
               for out, shape in zip(outs, out_shapes)):
      raise masking.ShapeError
    return tree_unflatten(out_tree(), outs)
  return wrapped_fun