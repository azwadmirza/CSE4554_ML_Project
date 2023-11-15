    def _get_primitive_value_str(self, member_type, value, import_tree=None):
        """
        Returns the nyan string representation of primitive values.

        Subroutine of _get_str_representation()
        """
        if member_type is MemberType.FLOAT:
            return f"{value}f"

        elif member_type in (MemberType.TEXT, MemberType.FILE):
            return f"\"{value}\""

        elif isinstance(member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(value.get_fqon()))

            else:
                sfqon = ".".join(value.get_fqon())

            return sfqon

        return f"{value}"