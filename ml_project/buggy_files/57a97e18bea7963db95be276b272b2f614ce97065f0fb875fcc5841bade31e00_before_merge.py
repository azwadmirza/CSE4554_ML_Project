    def __call__(self, typeinfer):
        with new_error_context("typing of setitem at {0}", self.loc):
            typevars = typeinfer.typevars
            if not all(typevars[var.name].defined
                       for var in (self.target, self.index, self.value)):
                return
            targetty = typevars[self.target.name].getone()
            idxty = typevars[self.index.name].getone()
            valty = typevars[self.value.name].getone()

            sig = typeinfer.context.resolve_setitem(targetty, idxty, valty)
            if sig is None:
                raise TypingError("Cannot resolve setitem: %s[%s] = %s" %
                                  (targetty, idxty, valty), loc=self.loc)
            self.signature = sig