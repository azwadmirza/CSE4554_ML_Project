  def sublift(self, val):
    return MaskTracer(self, val.val, val.shape_expr)