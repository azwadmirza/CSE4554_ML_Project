    def analyze_super(self, e: SuperExpr, is_lvalue: bool) -> Type:
        """Type check a super expression."""
        if e.info and e.info.bases:
            # TODO fix multiple inheritance etc
            if len(e.info.mro) < 2:
                self.chk.fail('Internal error: unexpected mro for {}: {}'.format(
                    e.info.name(), e.info.mro), e)
                return AnyType()
            for base in e.info.mro[1:]:
                if e.name in base.names or base == e.info.mro[-1]:
                    if e.info.fallback_to_any and base == e.info.mro[-1]:
                        # There's an undefined base class, and we're
                        # at the end of the chain.  That's not an error.
                        return AnyType()
                    if not self.chk.in_checked_function():
                        return AnyType()
                    args = self.chk.scope.top_function().arguments
                    # An empty args with super() is an error; we need something in declared_self
                    if not args:
                        self.chk.fail('super() requires at least one positional argument', e)
                        return AnyType()
                    declared_self = args[0].variable.type
                    return analyze_member_access(name=e.name, typ=fill_typevars(e.info), node=e,
                                                 is_lvalue=False, is_super=True, is_operator=False,
                                                 builtin_type=self.named_type,
                                                 not_ready_callback=self.not_ready_callback,
                                                 msg=self.msg, override_info=base,
                                                 original_type=declared_self, chk=self.chk)
            assert False, 'unreachable'
        else:
            # Invalid super. This has been reported by the semantic analyzer.
            return AnyType()