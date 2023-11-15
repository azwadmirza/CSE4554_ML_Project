    def process_type_info(self, info: TypeInfo) -> None:
        # TODO: Additional things:
        # - declared_metaclass
        # - metaclass_type
        # - _promote
        # - typeddict_type
        # - replaced
        replace_nodes_in_symbol_table(info.names, self.replacements)
        for i, item in enumerate(info.mro):
            info.mro[i] = self.fixup(info.mro[i])
        for i, base in enumerate(info.bases):
            self.fixup_type(info.bases[i])
        if info.tuple_type:
            self.fixup_type(info.tuple_type)