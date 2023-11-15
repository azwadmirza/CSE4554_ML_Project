    def i2h(self, pkt, x):
        return self._fixup_val(super(FlagsField, self).i2h(pkt, x))