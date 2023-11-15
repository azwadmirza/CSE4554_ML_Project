    def _get_str_representation(self, import_tree=None):
        """
        Returns the nyan string representation of the value.
        """
        if not self.is_initialized():
            return f"UNINITIALIZED VALUE {self.__repr__()}"

        if self._optional and self.value is MemberSpecialValue.NYAN_NONE:
            return MemberSpecialValue.NYAN_NONE.value

        if self.value is MemberSpecialValue.NYAN_INF:
            return MemberSpecialValue.NYAN_INF.value

        if self._member_type in (MemberType.INT, MemberType.FLOAT,
                                 MemberType.TEXT, MemberType.FILE,
                                 MemberType.BOOLEAN):
            return self._get_primitive_value_str(self._member_type,
                                                 self.value,
                                                 import_tree=import_tree)

        elif self._member_type in (MemberType.SET, MemberType.ORDEREDSET):
            output_str = ""

            if self._member_type is MemberType.ORDEREDSET:
                output_str += "o"

            output_str += "{"

            if len(self.value) > 0:
                for val in self.value:
                    output_str += "%s, " % self._get_primitive_value_str(
                        self._set_type,
                        val,
                        import_tree=import_tree
                    )

                return output_str[:-2] + "}"

            return output_str + "}"

        elif isinstance(self._member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(self.value.get_fqon()))

            else:
                sfqon = ".".join(self.value.get_fqon())

            return sfqon

        else:
            raise Exception(f"{self.__repr__()} has no valid type")