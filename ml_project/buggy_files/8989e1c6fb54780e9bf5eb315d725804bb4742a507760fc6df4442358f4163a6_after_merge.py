    def _check_late_binding_closure(self, node, assignment_node):
        if not self.linter.is_message_enabled("cell-var-from-loop"):
            return

        def _is_direct_lambda_call():
            return (
                isinstance(node_scope.parent, astroid.Call)
                and node_scope.parent.func is node_scope
            )

        node_scope = node.scope()
        if not isinstance(node_scope, (astroid.Lambda, astroid.FunctionDef)):
            return
        if isinstance(node.parent, astroid.Arguments):
            return

        if isinstance(assignment_node, astroid.Comprehension):
            if assignment_node.parent.parent_of(node.scope()):
                self.add_message("cell-var-from-loop", node=node, args=node.name)
        else:
            assign_scope = assignment_node.scope()
            maybe_for = assignment_node
            while maybe_for and not isinstance(maybe_for, astroid.For):
                if maybe_for is assign_scope:
                    break
                maybe_for = maybe_for.parent
            else:
                if (
                    maybe_for
                    and maybe_for.parent_of(node_scope)
                    and not _is_direct_lambda_call()
                    and not isinstance(node_scope.statement(), astroid.Return)
                ):
                    self.add_message("cell-var-from-loop", node=node, args=node.name)