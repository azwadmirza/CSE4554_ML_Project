def fuzz(p, _inplace=0):
    """
    Transform a layer into a fuzzy layer by replacing some default values
    by random objects.

    :param p: the Packet instance to fuzz
    :returns: the fuzzed packet.
    """
    if not _inplace:
        p = p.copy()
    q = p
    while not isinstance(q, NoPayload):
        new_default_fields = {}
        multiple_type_fields = []
        for f in q.fields_desc:
            if isinstance(f, PacketListField):
                for r in getattr(q, f.name):
                    print("fuzzing", repr(r))
                    fuzz(r, _inplace=1)
            elif isinstance(f, MultipleTypeField):
                # the type of the field will depend on others
                multiple_type_fields.append(f.name)
            elif f.default is not None:
                if not isinstance(f, ConditionalField) or f._evalcond(q):
                    rnd = f.randval()
                    if rnd is not None:
                        new_default_fields[f.name] = rnd
        # Process packets with MultipleTypeFields
        if multiple_type_fields:
            # freeze the other random values
            new_default_fields = {
                key: (val._fix() if isinstance(val, VolatileValue) else val)
                for key, val in six.iteritems(new_default_fields)
            }
            q.default_fields.update(new_default_fields)
            # add the random values of the MultipleTypeFields
            for name in multiple_type_fields:
                rnd = q.get_field(name)._find_fld_pkt(q).randval()
                if rnd is not None:
                    new_default_fields[name] = rnd
        q.default_fields.update(new_default_fields)
        q = q.payload
    return p