def reduce_translation_rule(c, operand, init_value, computation, jaxpr, consts, dimensions):
  xla_computation = _reduction_computation(c, jaxpr, consts, init_value)
  return c.Reduce(operand, init_value, xla_computation, dimensions)