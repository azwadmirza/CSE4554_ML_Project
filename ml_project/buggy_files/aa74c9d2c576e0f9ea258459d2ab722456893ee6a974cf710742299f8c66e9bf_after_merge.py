  def aval(self):
    return ShapedArray(self.shape_expr, self.val.dtype)