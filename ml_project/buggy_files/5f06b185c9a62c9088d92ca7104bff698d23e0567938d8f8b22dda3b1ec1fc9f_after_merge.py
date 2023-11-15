    def i2h(self, pkt, x):
        if isinstance(x, VolatileValue):
            return super(FlagsField, self).i2h(pkt, x)
        return self._fixup_val(super(FlagsField, self).i2h(pkt, x))