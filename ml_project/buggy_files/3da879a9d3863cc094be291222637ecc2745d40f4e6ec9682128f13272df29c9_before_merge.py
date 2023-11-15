    def check_second_pass(self, todo: Optional[List[DeferredNode]] = None) -> bool:
        """Run second or following pass of type checking.

        This goes through deferred nodes, returning True if there were any.
        """
        self.recurse_into_functions = True
        with experiments.strict_optional_set(self.options.strict_optional):
            if not todo and not self.deferred_nodes:
                return False
            self.errors.set_file(self.path, self.tree.fullname(), scope=self.tscope)
            self.tscope.enter_file(self.tree.fullname())
            self.pass_num += 1
            if not todo:
                todo = self.deferred_nodes
            else:
                assert not self.deferred_nodes
            self.deferred_nodes = []
            done = set()  # type: Set[Union[FuncDef, LambdaExpr, MypyFile, OverloadedFuncDef]]
            for node, type_name, active_typeinfo in todo:
                if node in done:
                    continue
                # This is useful for debugging:
                # print("XXX in pass %d, class %s, function %s" %
                #       (self.pass_num, type_name, node.fullname() or node.name()))
                done.add(node)
                with self.tscope.class_scope(active_typeinfo) if active_typeinfo else nothing():
                    with self.scope.push_class(active_typeinfo) if active_typeinfo else nothing():
                        self.check_partial(node)
            self.tscope.leave()
            return True