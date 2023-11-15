    def check_func_def(self, defn: FuncItem, typ: CallableType, name: str) -> None:
        """Type check a function definition."""
        # Expand type variables with value restrictions to ordinary types.
        for item, typ in self.expand_typevars(defn, typ):
            old_binder = self.binder
            self.binder = ConditionalTypeBinder()
            with self.binder.frame_context():
                defn.expanded.append(item)

                # We may be checking a function definition or an anonymous
                # function. In the first case, set up another reference with the
                # precise type.
                if isinstance(item, FuncDef):
                    fdef = item
                else:
                    fdef = None

                if fdef:
                    # Check if __init__ has an invalid, non-None return type.
                    if (fdef.info and fdef.name() == '__init__' and
                            not isinstance(typ.ret_type, (Void, NoneTyp)) and
                            not self.dynamic_funcs[-1]):
                        self.fail(messages.INIT_MUST_HAVE_NONE_RETURN_TYPE,
                                  item.type)

                    show_untyped = not self.is_typeshed_stub or self.options.warn_incomplete_stub
                    if self.options.disallow_untyped_defs and show_untyped:
                        # Check for functions with unspecified/not fully specified types.
                        def is_implicit_any(t: Type) -> bool:
                            return isinstance(t, AnyType) and t.implicit

                        if fdef.type is None:
                            self.fail(messages.FUNCTION_TYPE_EXPECTED, fdef)
                        elif isinstance(fdef.type, CallableType):
                            if is_implicit_any(fdef.type.ret_type):
                                self.fail(messages.RETURN_TYPE_EXPECTED, fdef)
                            if any(is_implicit_any(t) for t in fdef.type.arg_types):
                                self.fail(messages.ARGUMENT_TYPE_EXPECTED, fdef)

                if name in nodes.reverse_op_method_set:
                    self.check_reverse_op_method(item, typ, name)
                elif name == '__getattr__':
                    self.check_getattr_method(typ, defn)

                # Refuse contravariant return type variable
                if isinstance(typ.ret_type, TypeVarType):
                    if typ.ret_type.variance == CONTRAVARIANT:
                        self.fail(messages.RETURN_TYPE_CANNOT_BE_CONTRAVARIANT,
                             typ.ret_type)

                # Check that Generator functions have the appropriate return type.
                if defn.is_generator:
                    if not self.is_generator_return_type(typ.ret_type, defn.is_coroutine):
                        self.fail(messages.INVALID_RETURN_TYPE_FOR_GENERATOR, typ)

                    # Python 2 generators aren't allowed to return values.
                    if (self.options.python_version[0] == 2 and
                            isinstance(typ.ret_type, Instance) and
                            typ.ret_type.type.fullname() == 'typing.Generator'):
                        if not isinstance(typ.ret_type.args[2], (Void, NoneTyp, AnyType)):
                            self.fail(messages.INVALID_GENERATOR_RETURN_ITEM_TYPE, typ)

                # Fix the type if decorated with `@types.coroutine` or `@asyncio.coroutine`.
                if defn.is_awaitable_coroutine:
                    # Update the return type to AwaitableGenerator.
                    # (This doesn't exist in typing.py, only in typing.pyi.)
                    t = typ.ret_type
                    c = defn.is_coroutine
                    ty = self.get_generator_yield_type(t, c)
                    tc = self.get_generator_receive_type(t, c)
                    tr = self.get_generator_return_type(t, c)
                    ret_type = self.named_generic_type('typing.AwaitableGenerator',
                                                       [ty, tc, tr, t])
                    typ = typ.copy_modified(ret_type=ret_type)
                    defn.type = typ

                # Push return type.
                self.return_types.append(typ.ret_type)

                # Store argument types.
                for i in range(len(typ.arg_types)):
                    arg_type = typ.arg_types[i]

                    # Refuse covariant parameter type variables
                    if isinstance(arg_type, TypeVarType):
                        if arg_type.variance == COVARIANT:
                            self.fail(messages.FUNCTION_PARAMETER_CANNOT_BE_COVARIANT,
                                      arg_type)

                    if typ.arg_kinds[i] == nodes.ARG_STAR:
                        # builtins.tuple[T] is typing.Tuple[T, ...]
                        arg_type = self.named_generic_type('builtins.tuple',
                                                           [arg_type])
                    elif typ.arg_kinds[i] == nodes.ARG_STAR2:
                        arg_type = self.named_generic_type('builtins.dict',
                                                           [self.str_type(),
                                                            arg_type])
                    item.arguments[i].variable.type = arg_type

                # Type check initialization expressions.
                for arg in item.arguments:
                    init = arg.initialization_statement
                    if init:
                        self.accept(init)

            # Type check body in a new scope.
            with self.binder.frame_context():
                self.accept(item.body)

            self.return_types.pop()

            self.binder = old_binder