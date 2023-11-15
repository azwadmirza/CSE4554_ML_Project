    def imports_as_stmts(self, expr):
        """Convert the Result's imports to statements"""
        ret = Result()
        for module, names in self.imports.items():
            if None in names:
                ret += self.compile([
                    HyExpression([
                        HySymbol("import"),
                        HySymbol(module),
                    ]).replace(expr)
                ])
            names = sorted(name for name in names if name)
            if names:
                ret += self.compile([
                    HyExpression([
                        HySymbol("import"),
                        HyList([
                            HySymbol(module),
                            HyList([HySymbol(name) for name in names])
                        ])
                    ]).replace(expr)
                ])
        self.imports = defaultdict(set)
        return ret.stmts