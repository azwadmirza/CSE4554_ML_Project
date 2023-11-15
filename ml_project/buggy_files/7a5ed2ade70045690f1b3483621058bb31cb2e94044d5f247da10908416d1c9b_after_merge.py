    def visit_literal_type(self, typ: LiteralType) -> SnapshotItem:
        return ('LiteralType', snapshot_type(typ.fallback), typ.value)