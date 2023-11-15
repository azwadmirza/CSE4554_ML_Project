  def __mul__(self, other):
    coeffs = dict()
    for (mon1, coeff1), (mon2, coeff2) \
            in it.product(self.items(), ensure_poly(other).items()):
      mon = Mon(mon1 + mon2)                        # add monomials' id degrees
      coeff = coeff1 * coeff2                       # multiply integer coeffs
      coeffs[mon] = coeffs.get(mon, 0) + coeff  # accumulate coeffs

    return Poly(coeffs)