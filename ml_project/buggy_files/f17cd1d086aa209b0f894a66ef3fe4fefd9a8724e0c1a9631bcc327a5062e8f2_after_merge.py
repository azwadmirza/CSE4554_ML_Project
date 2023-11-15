  def __le__(self, other):
    return _ensure_poly(other) >= self