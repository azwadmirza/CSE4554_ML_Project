    def analyze_unbound_type_without_type_info(self, t: UnboundType, sym: SymbolTableNode,
                                               defining_literal: bool) -> Type:
        """Figure out what an unbound type that doesn't refer to a TypeInfo node means.

        This is something unusual. We try our best to find out what it is.
        """
        name = sym.fullname
        if name is None:
            assert sym.node is not None
            name = sym.node.name()
        # Option 1:
        # Something with an Any type -- make it an alias for Any in a type
        # context. This is slightly problematic as it allows using the type 'Any'
        # as a base class -- however, this will fail soon at runtime so the problem
        # is pretty minor.
        if isinstance(sym.node, Var) and isinstance(sym.node.type, AnyType):
            return AnyType(TypeOfAny.from_unimported_type,
                           missing_import_name=sym.node.type.missing_import_name)
        # Option 2:
        # Unbound type variable. Currently these may be still valid,
        # for example when defining a generic type alias.
        unbound_tvar = (isinstance(sym.node, TypeVarExpr) and
                        self.tvar_scope.get_binding(sym) is None)
        if self.allow_unbound_tvars and unbound_tvar:
            return t

        # Option 3:
        # Enum value. Note: we only want to return a LiteralType when
        # we're using this enum value specifically within context of
        # a "Literal[...]" type. So, if `defining_literal` is not set,
        # we bail out early with an error.
        #
        # If, in the distant future, we decide to permit things like
        # `def foo(x: Color.RED) -> None: ...`, we can remove that
        # check entirely.
        if isinstance(sym.node, Var) and sym.node.info and sym.node.info.is_enum:
            value = sym.node.name()
            base_enum_short_name = sym.node.info.name()
            if not defining_literal:
                msg = message_registry.INVALID_TYPE_RAW_ENUM_VALUE.format(
                    base_enum_short_name, value)
                self.fail(msg, t)
                return AnyType(TypeOfAny.from_error)
            return LiteralType(
                value=value,
                fallback=Instance(sym.node.info, [], line=t.line, column=t.column),
                line=t.line,
                column=t.column,
            )

        # None of the above options worked, we give up.
        self.fail('Invalid type "{}"'.format(name), t)

        # TODO: Would it be better to always return Any instead of UnboundType
        # in case of an error? On one hand, UnboundType has a name so error messages
        # are more detailed, on the other hand, some of them may be bogus.
        return t