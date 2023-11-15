    def add_local(self, node: Union[Var, FuncDef, OverloadedFuncDef], ctx: Context) -> None:
        assert self.locals[-1] is not None, "Should not add locals outside a function"
        name = node.name()
        if name in self.locals[-1]:
            self.name_already_defined(name, ctx, self.locals[-1][name])
        node._fullname = name
        self.locals[-1][name] = SymbolTableNode(LDEF, node)