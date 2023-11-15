    def __call__(self, typeinfer):
        with new_error_context("typing of static-get-item at {0}", self.loc):
            typevars = typeinfer.typevars
            oset = typevars[self.target]
            for ty in typevars[self.value.name].get():
                itemty = typeinfer.context.resolve_static_getitem(value=ty,
                                                                  index=self.index)
                if itemty is not None:
                    assert itemty.is_precise()
                    typeinfer.add_type(self.target, itemty, loc=self.loc)
                elif self.fallback is not None:
                    self.fallback(typeinfer)