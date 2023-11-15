    def visit_callable_type(self, left: CallableType) -> bool:
        right = self.right
        if isinstance(right, CallableType):
            return is_callable_compatible(
                left, right,
                is_compat=self._is_subtype,
                ignore_pos_arg_names=self.ignore_pos_arg_names)
        elif isinstance(right, Overloaded):
            return all(self._is_subtype(left, item) for item in right.items())
        elif isinstance(right, Instance):
            if right.type.is_protocol and right.type.protocol_members == ['__call__']:
                # OK, a callable can implement a protocol with a single `__call__` member.
                # TODO: we should probably explicitly exclude self-types in this case.
                call = find_member('__call__', right, left, is_operator=True)
                assert call is not None
                if self._is_subtype(left, call):
                    return True
            return self._is_subtype(left.fallback, right)
        elif isinstance(right, TypeType):
            # This is unsound, we don't check the __init__ signature.
            return left.is_type_obj() and self._is_subtype(left.ret_type, right.item)
        else:
            return False