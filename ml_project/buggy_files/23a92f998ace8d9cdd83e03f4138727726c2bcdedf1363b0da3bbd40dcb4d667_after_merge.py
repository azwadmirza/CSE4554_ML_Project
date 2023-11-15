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
    if cls.__module__ in sys.modules:
        # This makes typing.get_type_hints(CLS.__init__) resolve string types.
        globs.update(sys.modules[cls.__module__].__dict__)

    globs.update({"NOTHING": NOTHING, "attr_dict": attr_dict})

    if needs_cached_setattr:
        # Save the lookup overhead in __init__ if we need to circumvent
        # setattr hooks.
        globs["_cached_setattr"] = _obj_setattr

    init = _make_method(
        "__attrs_init__" if attrs_init else "__init__",
        script,
        unique_filename,
        globs,
    )
    init.__annotations__ = annotations

    return init