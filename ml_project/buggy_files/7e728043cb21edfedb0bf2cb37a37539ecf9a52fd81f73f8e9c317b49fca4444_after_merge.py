    def __sub__(self, other, **kwargs):
        return EDecimal(Decimal.__sub__(self, Decimal(other), **kwargs))