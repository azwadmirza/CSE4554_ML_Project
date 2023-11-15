  def is_pure(self):
    return all(type(poly) is not Poly or poly.is_constant for poly in self.shape_expr)