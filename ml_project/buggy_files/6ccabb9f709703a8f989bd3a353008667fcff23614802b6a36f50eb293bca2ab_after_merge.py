    def visit_instance(self, t: Instance) -> ProperType:
        if isinstance(self.s, Instance):
            si = self.s
            if t.type == si.type:
                if is_subtype(t, self.s) or is_subtype(self.s, t):
                    # Combine type arguments. We could have used join below
                    # equivalently.
                    args = []  # type: List[Type]
                    # N.B: We use zip instead of indexing because the lengths might have
                    # mismatches during daemon reprocessing.
                    for ta, sia in zip(t.args, si.args):
                        args.append(self.meet(ta, sia))
                    return Instance(t.type, args)
                else:
                    if state.strict_optional:
                        return UninhabitedType()
                    else:
                        return NoneType()
            else:
                if is_subtype(t, self.s):
                    return t
                elif is_subtype(self.s, t):
                    # See also above comment.
                    return self.s
                else:
                    if state.strict_optional:
                        return UninhabitedType()
                    else:
                        return NoneType()
        elif isinstance(self.s, FunctionLike) and t.type.is_protocol:
            call = unpack_callback_protocol(t)
            if call:
                return meet_types(call, self.s)
        elif isinstance(self.s, FunctionLike) and self.s.is_type_obj() and t.type.is_metaclass():
            if is_subtype(self.s.fallback, t):
                return self.s
            return self.default(self.s)
        elif isinstance(self.s, TypeType):
            return meet_types(t, self.s)
        elif isinstance(self.s, TupleType):
            return meet_types(t, self.s)
        elif isinstance(self.s, LiteralType):
            return meet_types(t, self.s)
        elif isinstance(self.s, TypedDictType):
            return meet_types(t, self.s)
        return self.default(self.s)