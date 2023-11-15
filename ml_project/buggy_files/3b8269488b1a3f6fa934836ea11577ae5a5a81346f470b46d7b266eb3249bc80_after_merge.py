    def dump(self, indent_depth, import_tree=None, namespace=None):
        """
        Returns the nyan string representation of the member.
        """
        output_str = f"{self.name}"

        type_str = ""

        if isinstance(self._member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(
                    self._member_type.get_fqon(),
                    namespace
                ))

            else:
                sfqon = ".".join(self._member_type.get_fqon())

            type_str = sfqon

        else:
            type_str = self._member_type.value

        if self._optional:
            output_str += f" : optional({type_str})"

        else:
            output_str += f" : {type_str}"

        if self.is_complex():
            if isinstance(self._set_type, NyanObject):
                if import_tree:
                    sfqon = ".".join(import_tree.get_alias_fqon(
                        self._set_type.get_fqon(),
                        namespace
                    ))

                else:
                    sfqon = ".".join(self._set_type.get_fqon())

                output_str += f"({sfqon})"

            else:
                output_str += f"({self._set_type.value})"

        if self.is_initialized():
            output_str += " %s%s %s" % ("@" * self._override_depth,
                                        self._operator.value,
                                        self._get_str_representation(
                                            indent_depth,
                                            import_tree=import_tree,
                                            namespace=namespace
                                        ))

        return output_str