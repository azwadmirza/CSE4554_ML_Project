    def node_should_be_modified(self, node):
        """Checks if the import statement imports ``get_image_uri`` from the correct module.

        Args:
            node (ast.ImportFrom): a node that represents a ``from ... import ... `` statement.
                For more, see https://docs.python.org/3/library/ast.html#abstract-grammar.

        Returns:
            bool: If the import statement imports ``get_image_uri`` from the correct module.
        """
        return (
            node is not None
            and node.module in GET_IMAGE_URI_NAMESPACES
            and any(name.name == GET_IMAGE_URI_NAME for name in node.names)
        )