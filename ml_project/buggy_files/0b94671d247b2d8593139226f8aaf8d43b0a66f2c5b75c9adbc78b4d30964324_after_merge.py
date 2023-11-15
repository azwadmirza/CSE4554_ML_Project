  def __rsub__(self, other):
    return _ensure_poly(other) - self