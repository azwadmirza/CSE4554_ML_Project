  def __init__(self, coeffs):
    # Makes sure Polynomials are always in canonical form
    coeffs = {mon: op.index(coeff) for mon, coeff in coeffs.items() if coeff != 0}
    coeffs = coeffs or {Mon(): 0}
    super().__init__(coeffs)