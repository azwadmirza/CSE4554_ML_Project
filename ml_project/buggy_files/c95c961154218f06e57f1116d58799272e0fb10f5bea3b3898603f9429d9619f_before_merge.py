def dt(name='', addr=None, obj = None):
    """
    Dump out a structure type Windbg style.
    """
    # Return value is a list of strings.of
    # We concatenate at the end.
    rv  = []

    if obj and not name:
        t = obj.type
        while t.code == (gdb.TYPE_CODE_PTR):
            t   = t.target()
            obj = obj.dereference()
        name = str(t)

    # Lookup the type name specified by the user
    else:
        t = pwndbg.typeinfo.load(name)

    # If it's not a struct (e.g. int or char*), bail
    if t.code not in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_TYPEDEF, gdb.TYPE_CODE_UNION):
        raise Exception("Not a structure: %s" % t)

    # If an address was specified, create a Value of the
    # specified type at that address.
    if addr is not None:
        obj = pwndbg.memory.poi(t, addr)

    # Header, optionally include the name
    header = name
    if obj: header = "%s @ %s" % (header, hex(int(obj.address)))
    rv.append(header)

    if t.strip_typedefs().code == gdb.TYPE_CODE_ARRAY:
        return "Arrays not supported yet"
    if t.strip_typedefs().code not in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION):
        t = {name: obj or gdb.Value(0).cast(t)}

    for name, field in t.items():
        # Offset into the parent structure
        o     = getattr(field, 'bitpos', 0)/8
        extra = str(field.type)
        ftype = field.type.strip_typedefs()

        if obj and obj.type.strip_typedefs().code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION):
            v  = obj[name]

            if ftype.code == gdb.TYPE_CODE_INT:
                v = hex(int(v))
            if ftype.code in (gdb.TYPE_CODE_PTR, gdb.TYPE_CODE_ARRAY) \
                and ftype.target() == pwndbg.typeinfo.uchar:
                data = pwndbg.memory.read(v.address, ftype.sizeof)
                v = ' '.join('%02x' % b for b in data)

            extra = v

        # Adjust trailing lines in 'extra' to line up
        # This is necessary when there are nested structures.
        # Ideally we'd expand recursively if the type is complex.
        extra_lines = []
        for i, line in enumerate(str(extra).splitlines()):
            if i == 0: extra_lines.append(line)
            else:      extra_lines.append(35*' ' + line)
        extra = '\n'.join(extra_lines)

        line  = "    +0x%04x %-20s : %s" % (o, name, extra)
        rv.append(line)

    return ('\n'.join(rv))