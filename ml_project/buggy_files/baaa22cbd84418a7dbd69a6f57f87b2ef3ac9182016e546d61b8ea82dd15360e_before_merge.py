def reduce_shape_rule(operand, init_value, jaxpr, consts, dimensions):
  return tuple(onp.delete(operand.shape, dimensions))