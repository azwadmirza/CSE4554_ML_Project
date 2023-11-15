    def try_infer_partial_type(self, e: CallExpr) -> None:
        if isinstance(e.callee, MemberExpr) and isinstance(e.callee.expr, RefExpr):
            var = cast(Var, e.callee.expr.node)
            partial_types = self.chk.find_partial_types(var)
            if partial_types is not None and not self.chk.current_node_deferred:
                partial_type = var.type
                if (partial_type is None or
                        not isinstance(partial_type, PartialType) or
                        partial_type.type is None):
                    # A partial None type -> can't infer anything.
                    return
                typename = partial_type.type.fullname()
                methodname = e.callee.name
                # Sometimes we can infer a full type for a partial List, Dict or Set type.
                # TODO: Don't infer argument expression twice.
                if (typename in self.item_args and methodname in self.item_args[typename]
                        and e.arg_kinds == [ARG_POS]):
                    item_type = self.accept(e.args[0])
                    full_item_type = UnionType.make_simplified_union(
                        [item_type, partial_type.inner_types[0]])
                    if mypy.checker.is_valid_inferred_type(full_item_type):
                        var.type = self.chk.named_generic_type(typename, [full_item_type])
                        del partial_types[var]
                elif (typename in self.container_args
                      and methodname in self.container_args[typename]
                      and e.arg_kinds == [ARG_POS]):
                    arg_type = self.accept(e.args[0])
                    if isinstance(arg_type, Instance):
                        arg_typename = arg_type.type.fullname()
                        if arg_typename in self.container_args[typename][methodname]:
                            full_item_types = [
                                UnionType.make_simplified_union([item_type, prev_type])
                                for item_type, prev_type
                                in zip(arg_type.args, partial_type.inner_types)
                            ]
                            if all(mypy.checker.is_valid_inferred_type(item_type)
                                   for item_type in full_item_types):
                                var.type = self.chk.named_generic_type(typename,
                                                                       list(full_item_types))
                                del partial_types[var]