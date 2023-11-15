    def __mod__(self, other, **kwargs):
        return EDecimal(Decimal.__mod__(self, Decimal(other), **kwargs))