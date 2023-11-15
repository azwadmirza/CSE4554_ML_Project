def get_output_types(*objs, unknown_as=None):
    output_types = []
    for obj in objs:
        if obj is None:
            continue
        elif isinstance(obj, (FuseChunk, FuseChunkData)):
            obj = obj.chunk

        try:
            output_types.append(_get_output_type_by_cls(type(obj)))
        except TypeError:
            if unknown_as is not None:
                output_types.append(unknown_as)
            else:  # pragma: no cover
                raise
    return output_types