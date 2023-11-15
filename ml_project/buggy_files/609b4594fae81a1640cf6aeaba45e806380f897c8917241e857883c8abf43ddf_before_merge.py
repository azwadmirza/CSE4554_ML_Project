    def __floordiv__(self, other, **kwargs):
        return EDecimal(Decimal.__floordiv__(self, other, **kwargs))