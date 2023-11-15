  def __gt__(self, other):
    return not (ensure_poly(other) >= self)