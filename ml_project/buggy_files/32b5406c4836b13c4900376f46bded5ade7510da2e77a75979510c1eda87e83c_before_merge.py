    def __call__(self, inst):
        if inst.domain is not self.last_domain:
            self.cache_position(inst.domain)
        value = inst[self.pos_cache]
        if self.values is None:
            return not isnan(value)
        else:
            return value in self.values