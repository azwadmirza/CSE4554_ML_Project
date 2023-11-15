    def set_value(self, val):
        for k in list(getattr(self, '_decl', {})):
            self.del_component(k)
        self._ctypes = {}
        self._decl = {}
        self._decl_order = []
        if val:
            for k in sorted(iterkeys(val)):
                self.add_component(k,val[k])