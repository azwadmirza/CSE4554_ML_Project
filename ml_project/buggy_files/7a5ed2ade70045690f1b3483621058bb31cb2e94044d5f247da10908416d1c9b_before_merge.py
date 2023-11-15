    def visit_literal_type(self, typ: LiteralType) -> SnapshotItem:
        return ('LiteralType', typ.value, snapshot_type(typ.fallback))