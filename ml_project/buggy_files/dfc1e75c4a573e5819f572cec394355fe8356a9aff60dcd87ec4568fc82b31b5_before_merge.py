    def to_var(self, info: TypeInfo) -> Var:
        return Var(self.name, info[self.name].type)