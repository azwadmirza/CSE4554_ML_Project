def reduce_shape_rule(operand, init_value, computation, jaxpr, consts, dimensions):
  return tuple(onp.delete(operand.shape, dimensions))