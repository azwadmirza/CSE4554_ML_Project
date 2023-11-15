    def _get_str_representation(self, indent_depth, import_tree=None, namespace=None):
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
            return self._get_primitive_value_str(
                self._member_type,
                self.value,
                import_tree=import_tree,
                namespace=namespace
            )

        elif self._member_type in (MemberType.SET, MemberType.ORDEREDSET):
            return self._get_complex_value_str(
                indent_depth,
                self._member_type,
                self.value,
                import_tree=import_tree,
                namespace=namespace
            )

        elif isinstance(self._member_type, NyanObject):
            if import_tree:
                sfqon = ".".join(import_tree.get_alias_fqon(
                    self.value.get_fqon(),
                    namespace
                ))

            else:
                sfqon = ".".join(self.value.get_fqon())

            return sfqon

        else:
            raise Exception(f"{self.__repr__()} has no valid type")