    def get_definition(self, value):
        """
        Get the definition site for the given variable name or instance.
        A Expr instance is returned.
        """
        while True:
            if isinstance(value, Var):
                name = value.name
            elif isinstance(value, str):
                name = value
            else:
                return value
            defs = self._definitions[name]
            if len(defs) == 0:
                raise KeyError("no definition for %r"
                               % (name,))
            if len(defs) > 1:
                raise KeyError("more than one definition for %r"
                               % (name,))
            value = defs[0]