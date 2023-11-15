def finalize_spec(spec, shape):
  return tuple(parse_lit(d) if e is monomorphic_dim else e
               for e, d in zip(spec, shape))