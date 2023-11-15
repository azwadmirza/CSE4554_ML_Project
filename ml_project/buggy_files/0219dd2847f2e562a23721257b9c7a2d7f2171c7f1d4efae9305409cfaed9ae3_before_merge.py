    def visit_attribute(self, node):
        """check if the getattr is an access to a class member
        if so, register it. Also check for access to protected
        class member from outside its class (but ignore __special__
        methods)
        """
        attrname = node.attrname
        # Check self
        if self.is_first_attr(node):
            self._accessed[-1][attrname].append(node)
            return
        if not self.linter.is_message_enabled('protected-access'):
            return

        self._check_protected_attribute_access(node)