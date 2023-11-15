    def check_reverse_op_method(self, defn: FuncItem, typ: CallableType,
                                method: str) -> None:
        """Check a reverse operator method such as __radd__."""

        # This used to check for some very obscure scenario.  It now
        # just decides whether it's worth calling
        # check_overlapping_op_methods().

        if method in ('__eq__', '__ne__'):
            # These are defined for all objects => can't cause trouble.
            return

        # With 'Any' or 'object' return type we are happy, since any possible
        # return value is valid.
        ret_type = typ.ret_type
        if isinstance(ret_type, AnyType):
            return
        if isinstance(ret_type, Instance):
            if ret_type.type.fullname() == 'builtins.object':
                return
        # Plausibly the method could have too few arguments, which would result
        # in an error elsewhere.
        if len(typ.arg_types) <= 2:
            # TODO check self argument kind

            # Check for the issue described above.
            arg_type = typ.arg_types[1]
            other_method = nodes.normal_from_reverse_op[method]
            if isinstance(arg_type, Instance):
                if not arg_type.type.has_readable_member(other_method):
                    return
            elif isinstance(arg_type, AnyType):
                return
            elif isinstance(arg_type, UnionType):
                if not arg_type.has_readable_member(other_method):
                    return
            else:
                return

            typ2 = self.expr_checker.analyze_external_member_access(
                other_method, arg_type, defn)
            self.check_overlapping_op_methods(
                typ, method, defn.info,
                typ2, other_method, cast(Instance, arg_type),
                defn)