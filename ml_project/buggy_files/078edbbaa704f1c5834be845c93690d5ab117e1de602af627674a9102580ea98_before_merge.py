    def visit_assignattr(self, node):
        if isinstance(node.assign_type(), astroid.AugAssign) and self.is_first_attr(node):
            self._accessed[-1][node.attrname].append(node)
        self._check_in_slots(node)