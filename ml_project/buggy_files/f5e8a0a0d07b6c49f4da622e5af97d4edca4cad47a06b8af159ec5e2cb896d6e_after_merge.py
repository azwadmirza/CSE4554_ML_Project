    def visit_call_expr(self, e: CallExpr, allow_none_return: bool = False) -> Type:
        """Type check a call expression."""
        if e.analyzed:
            # It's really a special form that only looks like a call.
            return self.accept(e.analyzed, self.type_context[-1])
        if isinstance(e.callee, NameExpr) and isinstance(e.callee.node, TypeInfo) and \
                e.callee.node.typeddict_type is not None:
            # Use named fallback for better error messages.
            typeddict_type = e.callee.node.typeddict_type.copy_modified(
                fallback=Instance(e.callee.node, []))
            return self.check_typeddict_call(typeddict_type, e.arg_kinds, e.arg_names, e.args, e)
        if (isinstance(e.callee, NameExpr) and e.callee.name in ('isinstance', 'issubclass')
                and len(e.args) == 2):
            for typ in mypy.checker.flatten(e.args[1]):
                if isinstance(typ, NameExpr):
                    try:
                        node = self.chk.lookup_qualified(typ.name)
                    except KeyError:
                        # Undefined names should already be reported in semantic analysis.
                        node = None
                if (isinstance(typ, IndexExpr)
                        and isinstance(typ.analyzed, (TypeApplication, TypeAliasExpr))
                        # node.kind == TYPE_ALIAS only for aliases like It = Iterable[int].
                        or isinstance(typ, NameExpr) and node and node.kind == nodes.TYPE_ALIAS):
                    self.msg.type_arguments_not_allowed(e)
        self.try_infer_partial_type(e)
        callee_type = self.accept(e.callee, always_allow_any=True)
        if (self.chk.options.disallow_untyped_calls and
                self.chk.in_checked_function() and
                isinstance(callee_type, CallableType)
                and callee_type.implicit):
            return self.msg.untyped_function_call(callee_type, e)
        # Figure out the full name of the callee for plugin loopup.
        object_type = None
        if not isinstance(e.callee, RefExpr):
            fullname = None
        else:
            fullname = e.callee.fullname
            if (fullname is None
                    and isinstance(e.callee, MemberExpr)
                    and isinstance(callee_type, FunctionLike)):
                # For method calls we include the defining class for the method
                # in the full name (example: 'typing.Mapping.get').
                callee_expr_type = self.chk.type_map.get(e.callee.expr)
                info = None
                # TODO: Support fallbacks of other kinds of types as well?
                if isinstance(callee_expr_type, Instance):
                    info = callee_expr_type.type
                elif isinstance(callee_expr_type, TypedDictType):
                    info = callee_expr_type.fallback.type.get_containing_type_info(e.callee.name)
                if info:
                    fullname = '{}.{}'.format(info.fullname(), e.callee.name)
                    object_type = callee_expr_type
                    # Apply plugin signature hook that may generate a better signature.
                    signature_hook = self.plugin.get_method_signature_hook(fullname)
                    if signature_hook:
                        callee_type = self.apply_method_signature_hook(
                            e, callee_type, object_type, signature_hook)
        ret_type = self.check_call_expr_with_callee_type(callee_type, e, fullname, object_type)
        if isinstance(ret_type, UninhabitedType):
            self.chk.binder.unreachable()
        if not allow_none_return and isinstance(ret_type, NoneTyp):
            self.chk.msg.does_not_return_value(callee_type, e)
            return AnyType(implicit=True)
        return ret_type