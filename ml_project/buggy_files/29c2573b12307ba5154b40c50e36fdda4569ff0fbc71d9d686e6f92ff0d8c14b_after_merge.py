    def check_func_def(self, defn: FuncItem, typ: CallableType, name: Optional[str]) -> None:
        """Type check a function definition."""
        # Expand type variables with value restrictions to ordinary types.
        expanded = self.expand_typevars(defn, typ)
        for item, typ in expanded:
            old_binder = self.binder
            self.binder = ConditionalTypeBinder()
            with self.binder.top_frame_context():
                defn.expanded.append(item)

                # We may be checking a function definition or an anonymous
                # function. In the first case, set up another reference with the
                # precise type.
                if isinstance(item, FuncDef):
                    fdef = item
                    # Check if __init__ has an invalid, non-None return type.
                    if (fdef.info and fdef.name() in ('__init__', '__init_subclass__') and
                            not isinstance(typ.ret_type, NoneType) and
                            not self.dynamic_funcs[-1]):
                        self.fail(message_registry.MUST_HAVE_NONE_RETURN_TYPE.format(fdef.name()),
                                  item)

                    # Check validity of __new__ signature
                    if fdef.info and fdef.name() == '__new__':
                        self.check___new___signature(fdef, typ)

                    self.check_for_missing_annotations(fdef)
                    if self.options.disallow_any_unimported:
                        if fdef.type and isinstance(fdef.type, CallableType):
                            ret_type = fdef.type.ret_type
                            if has_any_from_unimported_type(ret_type):
                                self.msg.unimported_type_becomes_any("Return type", ret_type, fdef)
                            for idx, arg_type in enumerate(fdef.type.arg_types):
                                if has_any_from_unimported_type(arg_type):
                                    prefix = "Argument {} to \"{}\"".format(idx + 1, fdef.name())
                                    self.msg.unimported_type_becomes_any(prefix, arg_type, fdef)
                    check_for_explicit_any(fdef.type, self.options, self.is_typeshed_stub,
                                           self.msg, context=fdef)

                if name:  # Special method names
                    if defn.info and self.is_reverse_op_method(name):
                        self.check_reverse_op_method(item, typ, name, defn)
                    elif name in ('__getattr__', '__getattribute__'):
                        self.check_getattr_method(typ, defn, name)
                    elif name == '__setattr__':
                        self.check_setattr_method(typ, defn)

                # Refuse contravariant return type variable
                if isinstance(typ.ret_type, TypeVarType):
                    if typ.ret_type.variance == CONTRAVARIANT:
                        self.fail(message_registry.RETURN_TYPE_CANNOT_BE_CONTRAVARIANT,
                             typ.ret_type)

                # Check that Generator functions have the appropriate return type.
                if defn.is_generator:
                    if defn.is_async_generator:
                        if not self.is_async_generator_return_type(typ.ret_type):
                            self.fail(message_registry.INVALID_RETURN_TYPE_FOR_ASYNC_GENERATOR,
                                      typ)
                    else:
                        if not self.is_generator_return_type(typ.ret_type, defn.is_coroutine):
                            self.fail(message_registry.INVALID_RETURN_TYPE_FOR_GENERATOR, typ)

                    # Python 2 generators aren't allowed to return values.
                    if (self.options.python_version[0] == 2 and
                            isinstance(typ.ret_type, Instance) and
                            typ.ret_type.type.fullname() == 'typing.Generator'):
                        if not isinstance(typ.ret_type.args[2], (NoneType, AnyType)):
                            self.fail(message_registry.INVALID_GENERATOR_RETURN_ITEM_TYPE, typ)

                # Fix the type if decorated with `@types.coroutine` or `@asyncio.coroutine`.
                if defn.is_awaitable_coroutine:
                    # Update the return type to AwaitableGenerator.
                    # (This doesn't exist in typing.py, only in typing.pyi.)
                    t = typ.ret_type
                    c = defn.is_coroutine
                    ty = self.get_generator_yield_type(t, c)
                    tc = self.get_generator_receive_type(t, c)
                    if c:
                        tr = self.get_coroutine_return_type(t)
                    else:
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
                    with self.scope.push_function(defn):
                        # We temporary push the definition to get the self type as
                        # visible from *inside* of this function/method.
                        ref_type = self.scope.active_self_type()  # type: Optional[Type]
                    if (isinstance(defn, FuncDef) and ref_type is not None and i == 0
                            and not defn.is_static
                            and typ.arg_kinds[0] not in [nodes.ARG_STAR, nodes.ARG_STAR2]):
                        isclass = defn.is_class or defn.name() in ('__new__', '__init_subclass__')
                        if isclass:
                            ref_type = mypy.types.TypeType.make_normalized(ref_type)
                        erased = erase_to_bound(arg_type)
                        if not is_subtype_ignoring_tvars(ref_type, erased):
                            note = None
                            if typ.arg_names[i] in ['self', 'cls']:
                                if (self.options.python_version[0] < 3
                                        and is_same_type(erased, arg_type) and not isclass):
                                    msg = message_registry.INVALID_SELF_TYPE_OR_EXTRA_ARG
                                    note = '(Hint: typically annotations omit the type for self)'
                                else:
                                    msg = message_registry.ERASED_SELF_TYPE_NOT_SUPERTYPE.format(
                                        erased, ref_type)
                            else:
                                msg = message_registry.MISSING_OR_INVALID_SELF_TYPE
                            self.fail(msg, defn)
                            if note:
                                self.note(note, defn)
                    elif isinstance(arg_type, TypeVarType):
                        # Refuse covariant parameter type variables
                        # TODO: check recursively for inner type variables
                        if (
                            arg_type.variance == COVARIANT and
                            defn.name() not in ('__init__', '__new__')
                        ):
                            ctx = arg_type  # type: Context
                            if ctx.line < 0:
                                ctx = typ
                            self.fail(message_registry.FUNCTION_PARAMETER_CANNOT_BE_COVARIANT, ctx)
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
                body_is_trivial = self.is_trivial_body(defn.body)
                for arg in item.arguments:
                    if arg.initializer is None:
                        continue
                    if body_is_trivial and isinstance(arg.initializer, EllipsisExpr):
                        continue
                    name = arg.variable.name()
                    msg = 'Incompatible default for '
                    if name.startswith('__tuple_arg_'):
                        msg += "tuple argument {}".format(name[12:])
                    else:
                        msg += 'argument "{}"'.format(name)
                    self.check_simple_assignment(arg.variable.type, arg.initializer,
                        context=arg, msg=msg, lvalue_name='argument', rvalue_name='default')

            # Type check body in a new scope.
            with self.binder.top_frame_context():
                with self.scope.push_function(defn):
                    # We suppress reachability warnings when we use TypeVars with value
                    # restrictions: we only want to report a warning if a certain statement is
                    # marked as being suppressed in *all* of the expansions, but we currently
                    # have no good way of doing this.
                    #
                    # TODO: Find a way of working around this limitation
                    if len(expanded) >= 2:
                        self.binder.suppress_unreachable_warnings()
                    self.accept(item.body)
                unreachable = self.binder.is_unreachable()

            if (self.options.warn_no_return and not unreachable):
                if (defn.is_generator or
                        is_named_instance(self.return_types[-1], 'typing.AwaitableGenerator')):
                    return_type = self.get_generator_return_type(self.return_types[-1],
                                                                 defn.is_coroutine)
                elif defn.is_coroutine:
                    return_type = self.get_coroutine_return_type(self.return_types[-1])
                else:
                    return_type = self.return_types[-1]

                if not isinstance(return_type, (NoneType, AnyType)) and not body_is_trivial:
                    # Control flow fell off the end of a function that was
                    # declared to return a non-None type and is not
                    # entirely pass/Ellipsis/raise NotImplementedError.
                    if isinstance(return_type, UninhabitedType):
                        # This is a NoReturn function
                        self.msg.fail(message_registry.INVALID_IMPLICIT_RETURN, defn)
                    else:
                        self.msg.fail(message_registry.MISSING_RETURN_STATEMENT, defn)

            self.return_types.pop()

            self.binder = old_binder