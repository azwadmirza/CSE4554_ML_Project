  def lift(self, val):
    return ShapeCheckTracer(self, onp.shape(val))