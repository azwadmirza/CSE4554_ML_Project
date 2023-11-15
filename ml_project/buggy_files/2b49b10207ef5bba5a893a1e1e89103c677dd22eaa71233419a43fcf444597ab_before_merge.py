    def to_argument(self, info: TypeInfo) -> Argument:
        return Argument(
            variable=self.to_var(info),
            type_annotation=info[self.name].type,
            initializer=None,
            kind=ARG_OPT if self.has_default else ARG_POS,
        )