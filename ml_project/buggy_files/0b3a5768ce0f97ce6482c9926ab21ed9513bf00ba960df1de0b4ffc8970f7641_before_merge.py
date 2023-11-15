    def try_infer_partial_type(self, e: CallExpr) -> None:
        partial_types = self.chk.partial_types[-1]
        if not partial_types:
            # Fast path leave -- no partial types in the current scope.
            return
        if isinstance(e.callee, MemberExpr) and isinstance(e.callee.expr, RefExpr):
            var = e.callee.expr.node
            if var in partial_types:
                var = cast(Var, var)
                partial_type_type = cast(PartialType, var.type).type
                if partial_type_type is None:
                    # A partial None type -> can't infer anything.
                    return
                typename = partial_type_type.fullname()
                methodname = e.callee.name
                # Sometimes we can infer a full type for a partial List, Dict or Set type.
                # TODO: Don't infer argument expression twice.
                if (typename in self.item_args and methodname in self.item_args[typename]
                        and e.arg_kinds == [ARG_POS]):
                    item_type = self.accept(e.args[0])
                    if mypy.checker.is_valid_inferred_type(item_type):
                        var.type = self.chk.named_generic_type(typename, [item_type])
                        del partial_types[var]
                elif (typename in self.container_args
                      and methodname in self.container_args[typename]
                      and e.arg_kinds == [ARG_POS]):
                    arg_type = self.accept(e.args[0])
                    if isinstance(arg_type, Instance):
                        arg_typename = arg_type.type.fullname()
                        if arg_typename in self.container_args[typename][methodname]:
                            if all(mypy.checker.is_valid_inferred_type(item_type)
                                   for item_type in arg_type.args):
                                var.type = self.chk.named_generic_type(typename,
                                                                       list(arg_type.args))
                                del partial_types[var]