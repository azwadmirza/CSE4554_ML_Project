    def __call__(self, typeinfer):
        with new_error_context("typing of argument at {0}", self.loc):
            typevars = typeinfer.typevars
            src = typevars[self.src]
            if not src.defined:
                return
            ty = src.getone()
            if isinstance(ty, types.Omitted):
                ty = typeinfer.context.resolve_value_type_prefer_literal(
                    ty.value,
                )
            if not ty.is_precise():
                raise TypingError('non-precise type {}'.format(ty))
            typeinfer.add_type(self.dst, ty, loc=self.loc)