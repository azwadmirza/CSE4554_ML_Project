    def visit_callable_type(self, typ: CallableType) -> SnapshotItem:
        # FIX generics
        return ('CallableType',
                snapshot_types(typ.arg_types),
                snapshot_type(typ.ret_type),
                tuple([encode_optional_str(name) for name in typ.arg_names]),
                tuple(typ.arg_kinds),
                typ.is_type_obj(),
                typ.is_ellipsis_args)