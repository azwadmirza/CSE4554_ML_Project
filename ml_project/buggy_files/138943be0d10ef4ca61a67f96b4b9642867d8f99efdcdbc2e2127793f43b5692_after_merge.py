  def __mul__(self, other):
    other = _ensure_poly(other)
    coeffs = {}
    for (mon1, coeff1), (mon2, coeff2) in product(self.items(), other.items()):
      mon = mon1 * mon2
      coeffs[mon] = coeffs.get(mon, 0) + coeff1 * coeff2
    return Poly(coeffs)