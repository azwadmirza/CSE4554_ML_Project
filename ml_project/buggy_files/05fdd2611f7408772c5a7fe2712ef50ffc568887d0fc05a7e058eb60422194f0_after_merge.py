    def _prepare_inheritance_content(self, import_tree=None):
        """
        Returns a string containing the nyan object's inheritance set
        in the header.

        Subroutine of dump().
        """
        output_str = "("

        if len(self._parents) > 0:
            for parent in self._parents:
                if import_tree:
                    sfqon = ".".join(import_tree.get_alias_fqon(
                        parent.get_fqon(),
                        namespace=self.get_fqon()
                    ))

                else:
                    sfqon = ".".join(parent.get_fqon())

                output_str += f"{sfqon}, "

            output_str = output_str[:-2]

        output_str += "):\n"

        return output_str