    def __add__(self, other, **kwargs):
        return EDecimal(Decimal.__add__(self, Decimal(other), **kwargs))