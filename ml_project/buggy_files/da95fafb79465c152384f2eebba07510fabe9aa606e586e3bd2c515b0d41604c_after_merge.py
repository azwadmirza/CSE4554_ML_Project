    def store(self, value, name, redefine=False):
        """
        Store *value* (a Expr or Var instance) into the variable named *name*
        (a str object). Returns the target variable.
        """
        if redefine or self.current_block_offset in self.cfa.backbone:
            rename = not (name in self.code_cellvars)
            target = self.current_scope.redefine(name, loc=self.loc, rename=rename)
        else:
            target = self.current_scope.get_or_define(name, loc=self.loc)
        if isinstance(value, ir.Var):
            value = self.assigner.assign(value, target)
        stmt = ir.Assign(value=value, target=target, loc=self.loc)
        self.current_block.append(stmt)
        self.definitions[target.name].append(value)
        return target