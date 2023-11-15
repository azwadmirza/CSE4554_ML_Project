    def visit_super_expr(self, e: SuperExpr) -> Type:
        """Type check a super expression (non-lvalue)."""

        # We have an expression like super(T, var).member

        # First compute the types of T and var
        types = self._super_arg_types(e)
        if isinstance(types, tuple):
            type_type, instance_type = types
        else:
            return types

        # Now get the MRO
        type_info = type_info_from_type(type_type)
        if type_info is None:
            self.chk.fail(message_registry.UNSUPPORTED_ARG_1_FOR_SUPER, e)
            return AnyType(TypeOfAny.from_error)

        instance_info = type_info_from_type(instance_type)
        if instance_info is None:
            self.chk.fail(message_registry.UNSUPPORTED_ARG_2_FOR_SUPER, e)
            return AnyType(TypeOfAny.from_error)

        mro = instance_info.mro

        # The base is the first MRO entry *after* type_info that has a member
        # with the right name
        try:
            index = mro.index(type_info)
        except ValueError:
            self.chk.fail(message_registry.SUPER_ARG_2_NOT_INSTANCE_OF_ARG_1, e)
            return AnyType(TypeOfAny.from_error)

        for base in mro[index+1:]:
            if e.name in base.names or base == mro[-1]:
                if e.info and e.info.fallback_to_any and base == mro[-1]:
                    # There's an undefined base class, and we're at the end of the
                    # chain.  That's not an error.
                    return AnyType(TypeOfAny.special_form)

                return analyze_member_access(name=e.name,
                                             typ=instance_type,
                                             is_lvalue=False,
                                             is_super=True,
                                             is_operator=False,
                                             original_type=instance_type,
                                             override_info=base,
                                             context=e,
                                             msg=self.msg,
                                             chk=self.chk,
                                             in_literal_context=self.is_literal_context())

        assert False, 'unreachable'