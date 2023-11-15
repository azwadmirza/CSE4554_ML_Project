def unop(result_dtype, accepted_dtypes, name, translation_rule=None):
  dtype_rule = partial(unop_dtype_rule, result_dtype, accepted_dtypes, name)
  prim = standard_primitive(_attrgetter('shape'), dtype_rule, name,
                            translation_rule=translation_rule)
  batching.defvectorized(prim)
  masking.defvectorized(prim)
  return prim