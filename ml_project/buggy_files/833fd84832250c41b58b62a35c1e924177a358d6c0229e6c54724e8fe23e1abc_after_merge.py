def shapecheck(in_shapes, out_shape, fun: Callable):
  _check_callable(fun)
  in_shapes, in_tree = tree_flatten(in_shapes)
  in_shapes = map(masking.parse_spec, in_shapes)
  out_shapes, out_tree = tree_flatten(out_shape)
  out_shapes = map(masking.parse_spec, out_shapes)
  flat_fun, out_tree_ = flatten_fun_nokwargs(lu.wrap_init(fun), in_tree)
  avals = map(partial(ShapedArray, dtype=onp.float32), in_shapes)
  out_shapes_ = [o.shape for o in pe.abstract_eval_fun(flat_fun.call_wrapped, *avals)]
  if out_tree != out_tree_(): raise TypeError("pytree mismatch")
  if not all(map(masking._shape_spec_consistent, out_shapes, out_shapes_)):
    raise masking.ShapeError
  return fun