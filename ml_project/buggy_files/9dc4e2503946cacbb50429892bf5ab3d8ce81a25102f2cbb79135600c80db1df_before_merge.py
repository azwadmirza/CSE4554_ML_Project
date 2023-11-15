def shape_as_value(expr):
  if type(expr) is tuple and is_polymorphic(expr):
    return tuple(eval_dim_expr(shape_envs.logical, d) if type(d) is Poly else d
                 for d in expr)
  else:
    return expr