    def _get_real_parent(self, node: Optional[ast.AST]) -> Optional[ast.AST]:
        """
        Returns real number's parent.

        What can go wrong?

        1. Number can be negative: ``x = -1``,
          so ``1`` has ``UnaryOp`` as parent, but should return ``Assign``

        """
        parent = getattr(node, 'wps_parent', None)
        if isinstance(parent, self._proxy_parents):
            return self._get_real_parent(parent)
        return parent