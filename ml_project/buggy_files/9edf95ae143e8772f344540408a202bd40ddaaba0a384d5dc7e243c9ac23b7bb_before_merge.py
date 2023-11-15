  def __add__(self, other):
    coeffs = self.copy()

    for mon, coeff in ensure_poly(other).items():
      coeffs[mon] = coeffs.get(mon, 0) + coeff

    return Poly(coeffs)