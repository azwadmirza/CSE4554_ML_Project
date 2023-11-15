    def _prepare_object_content(self, indent_depth, import_tree=None):
        """
        Returns a string containing the nyan object's content
        (members, nested objects).

        Subroutine of dump().
        """
        output_str = ""
        empty = True

        if len(self._inherited_members) > 0:
            for inherited_member in self._inherited_members:
                if inherited_member.has_value():
                    empty = False
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        inherited_member.dump(import_tree=import_tree)
                    )
            if not empty:
                output_str += "\n"

        if len(self._members) > 0:
            empty = False
            for member in self._members:
                if self.is_patch():
                    # Patches do not need the type definition
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        member.dump_short(import_tree=import_tree)
                    )
                else:
                    output_str += "%s%s\n" % (
                        (indent_depth + 1) * INDENT,
                        member.dump(import_tree=import_tree)
                    )

            output_str += "\n"

        # Nested objects
        if len(self._nested_objects) > 0:
            empty = False
            for nested_object in self._nested_objects:
                output_str += "%s%s" % (
                    (indent_depth + 1) * INDENT,
                    nested_object.dump(
                        indent_depth + 1,
                        import_tree
                    )
                )

            output_str += ""

        # Empty objects need a 'pass' line
        if empty:
            output_str += f"{(indent_depth + 1) * INDENT}pass\n\n"

        return output_str