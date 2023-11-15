    def dump_short(self, indent_depth, import_tree=None, namespace=None):
        """
        Returns the nyan string representation of the member, but
        without the type definition.
        """
        return "%s %s%s %s" % (
            self.get_name(),
            "@" * self._override_depth,
            self._operator.value,
            self._get_str_representation(
                indent_depth,
                import_tree=import_tree,
                namespace=namespace
            )
        )