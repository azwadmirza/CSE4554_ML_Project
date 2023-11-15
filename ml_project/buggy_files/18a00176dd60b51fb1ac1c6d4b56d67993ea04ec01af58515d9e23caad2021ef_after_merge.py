def _sort_translation_rule(c, *operands, dimension):
  types = [c.get_shape(x).xla_element_type() for x in operands]
  subc = xla_bridge.make_computation_builder("sort_lt_comparator")
  params = [xb.parameter(subc, 2 * i + j, xc.Shape.array_shape(typ, ()))
            for i, typ in enumerate(types) for j in range(2)]
  result = xla.lower_fun(_sort_lt_comparator,
                         multiple_results=False)(subc, *params)
  comparator = subc.build(result)
  out = xops.Sort(c, operands, dimension=dimension, is_stable=True,
                  comparator=comparator)
  return out if len(operands) != 1 else xops.Tuple(c, [out])