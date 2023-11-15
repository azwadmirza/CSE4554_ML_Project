  def process_primitive(self, primitive, tracers, params):
    avals = [t.aval for t in tracers]
    shape_rule = shape_rules.get(primitive)
    if shape_rule is None:
      raise NotImplementedError('Shape rule for {} not implemented yet.'.format(primitive))
    out_shape = shape_rule(*avals, **params)
    return ShapeCheckTracer(self, out_shape)