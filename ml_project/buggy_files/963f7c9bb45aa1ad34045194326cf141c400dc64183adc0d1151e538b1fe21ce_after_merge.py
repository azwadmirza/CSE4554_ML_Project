  def __gt__(self, other):
    return not (_ensure_poly(other) >= self)