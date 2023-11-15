    def visit_overloaded_func_def(self, node: OverloadedFuncDef) -> None:
        if not self.recurse_into_functions:
            return
        if node.impl:
            # Revert change made during semantic analysis pass 2.
            assert node.items[-1] is not node.impl
            node.items.append(node.impl)
        super().visit_overloaded_func_def(node)