def get_object(
    schema: s_schema.Schema,
    op: sd.ObjectCommand[so.Object],
    name: Optional[sn.Name] = None,
) -> so.Object:
    metaclass = op.get_schema_metaclass()
    if name is None:
        name = op.classname

    if issubclass(metaclass, s_types.Collection):
        if isinstance(name, sn.QualName):
            return schema.get(name)
        else:
            t_id = s_types.type_id_from_name(name)
            assert t_id is not None
            return schema.get_by_id(t_id)
    elif not issubclass(metaclass, so.QualifiedObject):
        obj = schema.get_global(metaclass, name)
        assert isinstance(obj, so.Object)
        return obj
    else:
        return schema.get(name)