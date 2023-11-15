    def __mul__(self, other, **kwargs):
        return EDecimal(Decimal.__mul__(self, other, **kwargs))