  def __le__(self, other):
    return ensure_poly(other) >= self