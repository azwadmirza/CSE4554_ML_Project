  def __divmod__(self, divisor):
    if self.is_constant:
      return divmod(int(self), divisor)
    else:
      def divided(count):
        q, r = divmod(count, divisor)
        if r != 0:
          raise ValueError('shapecheck currently only supports strides '
                          'that exactly divide the strided axis length.')
        return q

      return Poly(
        {k: coeff // divisor if k.degree == 0 else divided(coeff)
        for k, coeff in self.items()}), self.get(Mon(), 0) % divisor