def reduce(operand, init_value, computation, dimensions):
  monoid_reducer = _get_monoid_reducer(computation, init_value)
  if monoid_reducer:
    return monoid_reducer(operand, dimensions)
  else:
    jaxpr, consts = _reduction_jaxpr(computation, init_value)
    return reduce_p.bind(operand, init_value, computation=computation,
                         jaxpr=jaxpr, consts=consts, dimensions=tuple(dimensions))