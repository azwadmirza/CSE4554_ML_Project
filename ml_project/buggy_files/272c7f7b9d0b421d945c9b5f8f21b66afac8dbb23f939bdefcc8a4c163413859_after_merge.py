def _bind_shapes(shape_exprs, shapes):
  env = {}
  for shape_expr, shape in zip(shape_exprs, shapes):
    for poly, d in zip(shape_expr, shape):
      if type(poly) is not Poly or poly.is_constant:
        continue
      else:
        (binder,), = poly  # TODO generalize to handle striding
        if env.setdefault(binder, d) != d: raise masking.ShapeError
  return env