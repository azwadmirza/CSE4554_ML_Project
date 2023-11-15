  def lift(self, val):
    return MaskTracer(self, val, onp.shape(val))