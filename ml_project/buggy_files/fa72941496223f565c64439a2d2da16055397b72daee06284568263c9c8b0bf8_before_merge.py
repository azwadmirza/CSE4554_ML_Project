    def __call__(self, inst):
        if inst.domain is not self.last_domain:
            self.cache_position(inst.domain)
        value = inst[self.pos_cache]
        if self.case_sensitive:
            return value in self._values
        else:
            return value.lower() in self.values_lower