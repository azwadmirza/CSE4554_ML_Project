    def to_argument(self) -> Argument:
        return Argument(
            variable=self.to_var(),
            type_annotation=self.type,
            initializer=None,
            kind=ARG_OPT if self.has_default else ARG_POS,
        )