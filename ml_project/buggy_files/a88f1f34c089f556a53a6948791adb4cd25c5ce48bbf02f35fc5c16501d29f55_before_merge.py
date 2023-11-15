def parsed_instance_for(compiled: CompiledNode) -> ParsedNode:
    cls = PARSED_TYPES.get(compiled.resource_type)
    if cls is None:
        # how???
        raise ValueError('invalid resource_type: {}'
                         .format(compiled.resource_type))

    # validate=False to allow extra keys from copmiling
    return cls.from_dict(compiled.to_dict(), validate=False)