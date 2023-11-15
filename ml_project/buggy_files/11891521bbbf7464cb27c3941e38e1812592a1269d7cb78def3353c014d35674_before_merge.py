    def _export_from_type(self, t, contract, exported, list_contract):
        if isinstance(t, UserDefinedType):
            if isinstance(t.type, (Enum, Structure)):
                if t.type.contract != contract and t.type.contract not in exported:
                    self._export_list_used_contracts(t.type.contract, exported, list_contract)
            else:
                assert isinstance(t.type, Contract)
                if t.type != contract and t.type not in exported:
                    self._export_list_used_contracts(t.type, exported, list_contract)
        elif isinstance(t, MappingType):
            self._export_from_type(t.type_from, contract, exported, list_contract)
            self._export_from_type(t.type_to, contract, exported, list_contract)
        elif isinstance(t, ArrayType):
            self._export_from_type(t.type, contract, exported, list_contract)