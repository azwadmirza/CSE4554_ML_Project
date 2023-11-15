    def check_namedtuple(self,
                         node: Expression,
                         var_name: Optional[str],
                         is_func_scope: bool) -> Optional[TypeInfo]:
        """Check if a call defines a namedtuple.

        The optional var_name argument is the name of the variable to
        which this is assigned, if any.

        If it does, return the corresponding TypeInfo. Return None otherwise.

        If the definition is invalid but looks like a namedtuple,
        report errors but return (some) TypeInfo.
        """
        if not isinstance(node, CallExpr):
            return None
        call = node
        callee = call.callee
        if not isinstance(callee, RefExpr):
            return None
        fullname = callee.fullname
        if fullname == 'collections.namedtuple':
            is_typed = False
        elif fullname == 'typing.NamedTuple':
            is_typed = True
        else:
            return None
        items, types, defaults, ok = self.parse_namedtuple_args(call, fullname)
        if not ok:
            # Error. Construct dummy return value.
            return self.build_namedtuple_typeinfo('namedtuple', [], [], {})
        name = cast(StrExpr, call.args[0]).value
        if name != var_name or is_func_scope:
            # Give it a unique name derived from the line number.
            name += '@' + str(call.line)
        if len(defaults) > 0:
            default_items = {
                arg_name: default
                for arg_name, default in zip(items[-len(defaults):], defaults)
            }
        else:
            default_items = {}
        info = self.build_namedtuple_typeinfo(name, items, types, default_items)
        # Store it as a global just in case it would remain anonymous.
        # (Or in the nearest class if there is one.)
        stnode = SymbolTableNode(GDEF, info)
        self.api.add_symbol_table_node(name, stnode)
        call.analyzed = NamedTupleExpr(info, is_typed=is_typed)
        call.analyzed.set_line(call.line, call.column)
        return info