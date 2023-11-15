def _make_init(
    cls,
    attrs,
    pre_init,
    post_init,
    frozen,
    slots,
    cache_hash,
    base_attr_map,
    is_exc,
    has_global_on_setattr,
    attrs_init,
):
    if frozen and has_global_on_setattr:
        raise ValueError("Frozen classes can't use on_setattr.")

    needs_cached_setattr = cache_hash or frozen
    filtered_attrs = []
    attr_dict = {}
    for a in attrs:
        if not a.init and a.default is NOTHING:
            continue

        filtered_attrs.append(a)
        attr_dict[a.name] = a

        if a.on_setattr is not None:
            if frozen is True:
                raise ValueError("Frozen classes can't use on_setattr.")

            needs_cached_setattr = True
        elif (
            has_global_on_setattr and a.on_setattr is not setters.NO_OP
        ) or _is_slot_attr(a.name, base_attr_map):
            needs_cached_setattr = True

    unique_filename = _generate_unique_filename(cls, "init")

    script, globs, annotations = _attrs_to_init_script(
        filtered_attrs,
        frozen,
        slots,
        pre_init,
        post_init,
        cache_hash,
        base_attr_map,
        is_exc,
        needs_cached_setattr,
        has_global_on_setattr,
        attrs_init,
    )
    locs = {}
    bytecode = compile(script, unique_filename, "exec")
    globs.update({"NOTHING": NOTHING, "attr_dict": attr_dict})

    if needs_cached_setattr:
        # Save the lookup overhead in __init__ if we need to circumvent
        # setattr hooks.
        globs["_cached_setattr"] = _obj_setattr

    eval(bytecode, globs, locs)

    # In order of debuggers like PDB being able to step through the code,
    # we add a fake linecache entry.
    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    init = locs["__attrs_init__"] if attrs_init else locs["__init__"]
    init.__annotations__ = annotations

    return init