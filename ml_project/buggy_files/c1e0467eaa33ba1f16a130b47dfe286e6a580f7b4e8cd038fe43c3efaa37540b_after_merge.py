    def __div__(self, other, **kwargs):
        return EDecimal(Decimal.__div__(self, Decimal(other), **kwargs))