    def get_definition(self, value, lhs_only=False):
        """
        Get the definition site for the given variable name or instance.
        A Expr instance is returned by default, but if lhs_only is set
        to True, the left-hand-side variable is returned instead.
        """
        lhs = value
        while True:
            if isinstance(value, Var):
                lhs = value
                name = value.name
            elif isinstance(value, str):
                lhs = value
                name = value
            else:
                return lhs if lhs_only else value
            defs = self._definitions[name]
            if len(defs) == 0:
                raise KeyError("no definition for %r"
                               % (name,))
            if len(defs) > 1:
                raise KeyError("more than one definition for %r"
                               % (name,))
            value = defs[0]