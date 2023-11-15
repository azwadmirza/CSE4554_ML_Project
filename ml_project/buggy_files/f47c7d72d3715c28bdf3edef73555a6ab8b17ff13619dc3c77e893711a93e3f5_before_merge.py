  def __ge__(self, other):
    other = ensure_poly(other)

    if other.is_constant and self.is_constant:
      return int(self) >= int(other)

    if other.is_constant and int(other) <= 1:
        # Assume polynomials > 0, allowing to use shape rules of binops, conv:
        return True

    if self.is_constant and int(self) <= 0:
      return False # See above.

    if self == other:
      return True

    raise ValueError('Polynomials comparison "{} >= {}" is inconclusive.'
                     .format(self, other))