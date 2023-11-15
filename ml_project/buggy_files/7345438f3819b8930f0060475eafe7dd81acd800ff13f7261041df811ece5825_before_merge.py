  def __init__(self, coeffs):
    # Makes sure Polynomials are always in canonical form to simplify operators:
    coeffs = {mon: coeff for mon, coeff in coeffs.items() if coeff != 0}
    coeffs = {Mon(): 0} if len(coeffs) == 0 else coeffs
    super().__init__(coeffs)