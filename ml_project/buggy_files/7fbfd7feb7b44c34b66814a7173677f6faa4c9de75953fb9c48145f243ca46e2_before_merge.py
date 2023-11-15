  def is_pure(self):
    return all(ensure_poly(poly).is_constant for poly in self.shape_expr)