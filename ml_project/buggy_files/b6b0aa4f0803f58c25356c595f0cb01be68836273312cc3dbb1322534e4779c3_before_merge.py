  def __divmod__(self, divisor):
    if self.is_constant:
      q, r = divmod(int(self), divisor)

      return constant_poly(q), r

    def divided(count):
      q, r = divmod(count, divisor)
      if r != 0:
        raise ValueError('shapecheck currently only supports strides '
                         'that exactly divide the strided axis length.')
      return q

    return Poly(
      {k: coeff // divisor if k.degree == 0 else divided(coeff)
      for k, coeff in self.items()}), self[Mon()] % divisor