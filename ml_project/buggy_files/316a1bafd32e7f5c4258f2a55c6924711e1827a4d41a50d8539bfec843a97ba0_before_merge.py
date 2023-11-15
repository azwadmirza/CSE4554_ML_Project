def get_output_types(*objs, unknown_as=None):
    output_types = []
    for obj in objs:
        if obj is None:
            continue
        for tp in OutputType.__members__.values():
            try:
                tileable_types = _OUTPUT_TYPE_TO_TILEABLE_TYPES[tp]
                chunk_types = _OUTPUT_TYPE_TO_CHUNK_TYPES[tp]
                if isinstance(obj, (tileable_types, chunk_types)):
                    output_types.append(tp)
                    break
            except KeyError:
                continue
        else:
            if unknown_as is not None:
                output_types.append(unknown_as)
            else:  # pragma: no cover
                raise TypeError('Output can only be tensor, dataframe or series')
    return output_types