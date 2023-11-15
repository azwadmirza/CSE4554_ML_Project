def _remap_ids(names, shape_spec):
  ShapeSpec, Poly, Mon = masking.ShapeSpec, masking.Poly, masking.Mon
  mdim = masking.monomorphic_dim
  return ShapeSpec(Poly({Mon({names[id] : deg for id, deg in mon.items()})
                          : coeff for mon, coeff in poly.items()})
                   if poly is not mdim else mdim for poly in shape_spec)