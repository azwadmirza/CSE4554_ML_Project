def fuzz(p, _inplace=0):
    """Transform a layer into a fuzzy layer by replacing some default values by random objects"""  # noqa: E501
    if not _inplace:
        p = p.copy()
    q = p
    while not isinstance(q, NoPayload):
        for f in q.fields_desc:
            if isinstance(f, PacketListField):
                for r in getattr(q, f.name):
                    print("fuzzing", repr(r))
                    fuzz(r, _inplace=1)
            elif f.default is not None:
                if not isinstance(f, ConditionalField) or f._evalcond(q):
                    rnd = f.randval()
                    if rnd is not None:
                        q.default_fields[f.name] = rnd
        q = q.payload
    return p