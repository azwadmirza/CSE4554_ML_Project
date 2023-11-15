    def is_assigned(self, node):
        assigned = False
        if self.ignore_nodes:
            if isinstance(self.ignore_nodes, (list, tuple, object)):
                if isinstance(node, self.ignore_nodes):
                    return assigned

        if isinstance(node, ast.Expr):
            assigned = self.is_assigned(node.value)
        elif isinstance(node, ast.FunctionDef):
            for name in node.args.args:
                if isinstance(name, ast.Name):
                    if name.id == self.var_name.id:
                        # If is param the assignations are not affected
                        return assigned
            assigned = self.is_assigned_in(node.body)
        elif isinstance(node, ast.With):
            if node.optional_vars.id == self.var_name.id:
                assigned = node
            else:
                assigned = self.is_assigned_in(node.body)
        elif isinstance(node, ast.TryFinally):
            assigned = []
            assigned.extend(self.is_assigned_in(node.body))
            assigned.extend(self.is_assigned_in(node.finalbody))
        elif isinstance(node, ast.TryExcept):
            assigned = []
            assigned.extend(self.is_assigned_in(node.body))
            assigned.extend(self.is_assigned_in(node.handlers))
            assigned.extend(self.is_assigned_in(node.orelse))
        elif isinstance(node, ast.ExceptHandler):
            assigned = []
            assigned.extend(self.is_assigned_in(node.body))
        elif isinstance(node, (ast.If, ast.For, ast.While)):
            assigned = []
            assigned.extend(self.is_assigned_in(node.body))
            assigned.extend(self.is_assigned_in(node.orelse))
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                if node.target.id == self.var_name.id:
                    assigned = node.value
        elif isinstance(node, ast.Assign) and node.targets:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                if target.id == self.var_name.id:
                    assigned = node.value
            elif isinstance(target, ast.Tuple):
                pos = 0
                for name in target.elts:
                    if name.id == self.var_name.id:
                        assigned = node.value.elts[pos]
                        break
                    pos += 1
        return assigned