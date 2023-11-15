    def imports_as_stmts(self, expr):
        """Convert the Result's imports to statements"""
        ret = Result()
        for module, names in self.imports.items():
            if None in names:
                e = HyExpression([
                        HySymbol("import"),
                        HySymbol(module),
                    ]).replace(expr)
                spoof_positions(e)
                ret += self.compile(e)
            names = sorted(name for name in names if name)
            if names:
                e = HyExpression([
                        HySymbol("import"),
                        HyList([
                            HySymbol(module),
                            HyList([HySymbol(name) for name in names])
                        ])
                    ]).replace(expr)
                spoof_positions(e)
                ret += self.compile(e)
        self.imports = defaultdict(set)
        return ret.stmts