    def accept(self,
               node: Expression,
               type_context: Optional[Type] = None,
               allow_none_return: bool = False,
               always_allow_any: bool = False,
               ) -> Type:
        """Type check a node in the given type context.  If allow_none_return
        is True and this expression is a call, allow it to return None.  This
        applies only to this expression and not any subexpressions.
        """
        if node in self.type_overrides:
            return self.type_overrides[node]
        self.type_context.append(type_context)
        try:
            if allow_none_return and isinstance(node, CallExpr):
                typ = self.visit_call_expr(node, allow_none_return=True)
            elif allow_none_return and isinstance(node, YieldFromExpr):
                typ = self.visit_yield_from_expr(node, allow_none_return=True)
            elif allow_none_return and isinstance(node, ConditionalExpr):
                typ = self.visit_conditional_expr(node, allow_none_return=True)
            else:
                typ = node.accept(self)
        except Exception as err:
            report_internal_error(err, self.chk.errors.file,
                                  node.line, self.chk.errors, self.chk.options)

        self.type_context.pop()
        assert typ is not None
        self.chk.store_type(node, typ)

        if isinstance(node, AssignmentExpr) and not has_uninhabited_component(typ):
            self.chk.store_type(node.target, typ)

        if (self.chk.options.disallow_any_expr and
                not always_allow_any and
                not self.chk.is_stub and
                self.chk.in_checked_function() and
                has_any_type(typ) and not self.chk.current_node_deferred):
            self.msg.disallowed_any_type(typ, node)

        if not self.chk.in_checked_function() or self.chk.current_node_deferred:
            return AnyType(TypeOfAny.unannotated)
        else:
            return typ