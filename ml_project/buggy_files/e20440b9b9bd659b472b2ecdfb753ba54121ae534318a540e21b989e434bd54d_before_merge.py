  def pure(self, val):
    return ShapeCheckTracer(self, onp.shape(val))