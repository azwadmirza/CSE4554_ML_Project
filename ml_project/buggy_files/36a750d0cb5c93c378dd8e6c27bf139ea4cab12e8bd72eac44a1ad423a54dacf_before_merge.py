    def ann_assign(self):
        self.context.set_in_assignment(True)
        typ = parse_type(self.stmt.annotation, location='memory', custom_units=self.context.custom_units)
        if isinstance(self.stmt.target, ast.Attribute) and self.stmt.target.value.id == 'self':
            raise TypeMismatchException('May not redefine storage variables.', self.stmt)
        varname = self.stmt.target.id
        pos = self.context.new_variable(varname, typ)
        o = LLLnode.from_list('pass', typ=None, pos=pos)
        if self.stmt.value is not None:
            sub = Expr(self.stmt.value, self.context).lll_node
            self._check_valid_assign(sub)
            self._check_same_variable_assign(sub)
            variable_loc = LLLnode.from_list(pos, typ=typ, location='memory', pos=getpos(self.stmt))
            o = make_setter(variable_loc, sub, 'memory', pos=getpos(self.stmt))
        self.context.set_in_assignment(False)
        return o