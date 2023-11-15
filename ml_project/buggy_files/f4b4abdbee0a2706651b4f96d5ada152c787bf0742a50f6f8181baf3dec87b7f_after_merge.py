    def visit_overloaded_func_def(self, node: OverloadedFuncDef) -> None:
        if not self.recurse_into_functions:
            return
        # Revert change made during semantic analysis pass 2.
        node.items = node.unanalyzed_items.copy()
        super().visit_overloaded_func_def(node)