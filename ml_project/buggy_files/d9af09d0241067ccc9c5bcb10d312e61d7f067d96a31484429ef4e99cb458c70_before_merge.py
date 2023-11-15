    def dump_short(self, import_tree=None):
        """
        Returns the nyan string representation of the member, but
        without the type definition.
        """
        return "%s %s%s %s" % (self.get_name(),
                               "@" * self._override_depth,
                               self._operator.value,
                               self._get_str_representation(import_tree=import_tree))