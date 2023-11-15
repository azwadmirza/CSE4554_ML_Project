def _remap_ids(names, shape_spec):
  return masking.ShapeSpec(Poly({Mon({names[id] : deg for id, deg in mon.items()})
                          : coeff for mon, coeff in poly.items()})
                   if poly is not masking._monomorphic_dim else
                   masking._monomorphic_dim for poly in shape_spec)