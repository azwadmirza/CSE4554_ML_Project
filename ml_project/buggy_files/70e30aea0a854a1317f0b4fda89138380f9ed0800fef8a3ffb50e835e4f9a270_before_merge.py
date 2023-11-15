    def set_value(self, val):
        _indicator_var = self.indicator_var
        # Remove everything
        for k in list(getattr(self, '_decl', {})):
            self.del_component(k)
        self._ctypes = {}
        self._decl = {}
        self._decl_order = []
        # Now copy over everything from the other block.  If the other
        # block has an indicator_var, it should override this block's.
        # Otherwise restore this block's indicator_var.
        if val:
            if 'indicator_var' not in val:
                self.add_component('indicator_var', _indicator_var)
            for k in sorted(iterkeys(val)):
                self.add_component(k,val[k])
        else:
            self.add_component('indicator_var', _indicator_var)