  def sublift(self, val):
    return ShapeCheckTracer(self, val.shape_expr)