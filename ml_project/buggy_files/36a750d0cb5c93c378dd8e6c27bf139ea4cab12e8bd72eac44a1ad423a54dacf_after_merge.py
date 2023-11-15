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
            # If bytes[32] to bytes32 assignment rewrite sub as bytes32.
            if isinstance(sub.typ, ByteArrayType) and sub.typ.maxlen == 32 and isinstance(typ, BaseType) and typ.typ == 'bytes32':
                bytez, bytez_length = string_to_bytes(self.stmt.value.s)
                sub = LLLnode(bytes_to_int(bytez), typ=BaseType('bytes32'), pos=getpos(self.stmt))
            self._check_valid_assign(sub)
            self._check_same_variable_assign(sub)
            variable_loc = LLLnode.from_list(pos, typ=typ, location='memory', pos=getpos(self.stmt))
            o = make_setter(variable_loc, sub, 'memory', pos=getpos(self.stmt))
        self.context.set_in_assignment(False)
        return o