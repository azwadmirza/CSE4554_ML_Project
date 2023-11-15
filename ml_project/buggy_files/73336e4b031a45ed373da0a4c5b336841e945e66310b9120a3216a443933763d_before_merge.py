    def visit_unbound_type(self, t: UnboundType) -> Type:
        if t.optional:
            t.optional = False
            # We don't need to worry about double-wrapping Optionals or
            # wrapping Anys: Union simplification will take care of that.
            return make_optional_type(self.visit_unbound_type(t))
        sym = self.lookup(t.name, t)
        if sym is not None:
            if sym.node is None:
                # UNBOUND_IMPORTED can happen if an unknown name was imported.
                if sym.kind != UNBOUND_IMPORTED:
                    self.fail('Internal error (node is None, kind={})'.format(sym.kind), t)
                return AnyType(TypeOfAny.special_form)
            fullname = sym.node.fullname()
            hook = self.plugin.get_type_analyze_hook(fullname)
            if hook:
                return hook(AnalyzeTypeContext(t, t, self))
            if (fullname in nongen_builtins and t.args and
                    not sym.normalized and not self.allow_unnormalized):
                self.fail(no_subscript_builtin_alias(fullname), t)
            tvar_def = self.tvar_scope.get_binding(sym)
            if sym.kind == TVAR and tvar_def is not None:
                if len(t.args) > 0:
                    self.fail('Type variable "{}" used with arguments'.format(
                        t.name), t)
                return TypeVarType(tvar_def, t.line)
            elif fullname == 'builtins.None':
                return NoneTyp()
            elif fullname == 'typing.Any' or fullname == 'builtins.Any':
                return AnyType(TypeOfAny.explicit)
            elif fullname == 'typing.Tuple':
                if len(t.args) == 0 and not t.empty_tuple_index:
                    # Bare 'Tuple' is same as 'tuple'
                    if 'generics' in self.options.disallow_any and not self.is_typeshed_stub:
                        self.fail(messages.BARE_GENERIC, t)
                    typ = self.named_type('builtins.tuple', line=t.line, column=t.column)
                    typ.from_generic_builtin = True
                    return typ
                if len(t.args) == 2 and isinstance(t.args[1], EllipsisType):
                    # Tuple[T, ...] (uniform, variable-length tuple)
                    instance = self.named_type('builtins.tuple', [self.anal_type(t.args[0])])
                    instance.line = t.line
                    return instance
                return self.tuple_type(self.anal_array(t.args))
            elif fullname == 'typing.Union':
                items = self.anal_array(t.args)
                return UnionType.make_union(items)
            elif fullname == 'typing.Optional':
                if len(t.args) != 1:
                    self.fail('Optional[...] must have exactly one type argument', t)
                    return AnyType(TypeOfAny.from_error)
                item = self.anal_type(t.args[0])
                return make_optional_type(item)
            elif fullname == 'typing.Callable':
                return self.analyze_callable_type(t)
            elif fullname == 'typing.Type':
                if len(t.args) == 0:
                    any_type = AnyType(TypeOfAny.from_omitted_generics,
                                       line=t.line, column=t.column)
                    return TypeType(any_type, line=t.line, column=t.column)
                if len(t.args) != 1:
                    self.fail('Type[...] must have exactly one type argument', t)
                item = self.anal_type(t.args[0])
                return TypeType.make_normalized(item, line=t.line)
            elif fullname == 'typing.ClassVar':
                if self.nesting_level > 0:
                    self.fail('Invalid type: ClassVar nested inside other type', t)
                if len(t.args) == 0:
                    return AnyType(TypeOfAny.from_omitted_generics, line=t.line, column=t.column)
                if len(t.args) != 1:
                    self.fail('ClassVar[...] must have at most one type argument', t)
                    return AnyType(TypeOfAny.from_error)
                item = self.anal_type(t.args[0])
                if isinstance(item, TypeVarType) or get_type_vars(item):
                    self.fail('Invalid type: ClassVar cannot be generic', t)
                    return AnyType(TypeOfAny.from_error)
                return item
            elif fullname in ('mypy_extensions.NoReturn', 'typing.NoReturn'):
                return UninhabitedType(is_noreturn=True)
            elif sym.kind == TYPE_ALIAS:
                override = sym.type_override
                all_vars = sym.alias_tvars
                assert override is not None
                an_args = self.anal_array(t.args)
                if all_vars is not None:
                    exp_len = len(all_vars)
                else:
                    exp_len = 0
                act_len = len(an_args)
                if exp_len > 0 and act_len == 0:
                    # Interpret bare Alias same as normal generic, i.e., Alias[Any, Any, ...]
                    assert all_vars is not None
                    return set_any_tvars(override, all_vars, t.line, t.column)
                if exp_len == 0 and act_len == 0:
                    return override
                if act_len != exp_len:
                    self.fail('Bad number of arguments for type alias, expected: %s, given: %s'
                              % (exp_len, act_len), t)
                    return set_any_tvars(override, all_vars or [],
                                         t.line, t.column, implicit=False)
                assert all_vars is not None
                return replace_alias_tvars(override, all_vars, an_args, t.line, t.column)
            elif not isinstance(sym.node, TypeInfo):
                name = sym.fullname
                if name is None:
                    name = sym.node.name()
                if isinstance(sym.node, Var) and isinstance(sym.node.type, AnyType):
                    # Something with an Any type -- make it an alias for Any in a type
                    # context. This is slightly problematic as it allows using the type 'Any'
                    # as a base class -- however, this will fail soon at runtime so the problem
                    # is pretty minor.
                    return AnyType(TypeOfAny.from_unimported_type)
                # Allow unbound type variables when defining an alias
                if not (self.aliasing and sym.kind == TVAR and
                        self.tvar_scope.get_binding(sym) is None):
                    self.fail('Invalid type "{}"'.format(name), t)
                return t
            info = sym.node  # type: TypeInfo
            if len(t.args) > 0 and info.fullname() == 'builtins.tuple':
                fallback = Instance(info, [AnyType(TypeOfAny.special_form)], t.line)
                return TupleType(self.anal_array(t.args), fallback, t.line)
            else:
                # Analyze arguments and construct Instance type. The
                # number of type arguments and their values are
                # checked only later, since we do not always know the
                # valid count at this point. Thus we may construct an
                # Instance with an invalid number of type arguments.
                instance = Instance(info, self.anal_array(t.args), t.line, t.column)
                instance.from_generic_builtin = sym.normalized
                tup = info.tuple_type
                if tup is not None:
                    # The class has a Tuple[...] base class so it will be
                    # represented as a tuple type.
                    if t.args:
                        self.fail('Generic tuple types not supported', t)
                        return AnyType(TypeOfAny.from_error)
                    return tup.copy_modified(items=self.anal_array(tup.items),
                                             fallback=instance)
                td = info.typeddict_type
                if td is not None:
                    # The class has a TypedDict[...] base class so it will be
                    # represented as a typeddict type.
                    if t.args:
                        self.fail('Generic TypedDict types not supported', t)
                        return AnyType(TypeOfAny.from_error)
                    # Create a named TypedDictType
                    return td.copy_modified(item_types=self.anal_array(list(td.items.values())),
                                            fallback=instance)
                return instance
        else:
            return AnyType(TypeOfAny.special_form)