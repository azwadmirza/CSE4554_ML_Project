    def __divmod__(self, other, **kwargs):
        return EDecimal(Decimal.__divmod__(self, Decimal(other), **kwargs))