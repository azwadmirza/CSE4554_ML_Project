  def __ge__(self, other):
    other = _ensure_poly(other)

    if other.is_constant and self.is_constant:
      return int(self) >= int(other)
    elif other.is_constant and int(other) <= 1:
      # Assume nonzero polynomials are positive, allows use in shape rules
      return True
    elif self.is_constant and int(self) <= 0:
      return False  # See above.
    elif self == other:
      return True

    raise ValueError('Polynomials comparison "{} >= {}" is inconclusive.'
                     .format(self, other))