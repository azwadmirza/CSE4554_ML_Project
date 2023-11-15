    def visit_instance(self, typ: Instance) -> SnapshotItem:
        return ('Instance',
                typ.type.fullname(),
                snapshot_types(typ.args),
                None if typ.last_known_value is None else snapshot_type(typ.last_known_value))