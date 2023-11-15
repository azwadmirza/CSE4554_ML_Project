    def op_MAKE_FUNCTION(self, inst, name, code, closure, annotations, kwdefaults, defaults, res):
        if annotations != None:
            raise NotImplementedError("op_MAKE_FUNCTION with annotations is not implemented")
        if kwdefaults != None:
            raise NotImplementedError("op_MAKE_FUNCTION with kwdefaults is not implemented")
        if defaults:
            if isinstance(defaults, tuple):
                defaults = tuple([self.get(name) for name in defaults])
            else:
                defaults = self.get(defaults)
        fcode = self.definitions[code][0].value
        if name:
            name = self.get(name)
        if closure:
            closure = self.get(closure)
        expr = ir.Expr.make_function(name, fcode, closure, defaults, self.loc)
        self.store(expr, res)