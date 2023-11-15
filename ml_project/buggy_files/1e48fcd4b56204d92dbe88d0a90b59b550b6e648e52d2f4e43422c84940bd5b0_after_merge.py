    def __truediv__(self, other, **kwargs):
        return EDecimal(Decimal.__truediv__(self, Decimal(other), **kwargs))