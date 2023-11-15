    def __pow__(self, other, **kwargs):
        return EDecimal(Decimal.__pow__(self, Decimal(other), **kwargs))