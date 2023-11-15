def get_dataclass_data(
    obj: Any, allow_objects: Optional[bool] = None
) -> Dict[str, Any]:
    from omegaconf.omegaconf import MISSING, OmegaConf, _maybe_wrap

    flags = {"allow_objects": allow_objects} if allow_objects is not None else {}
    dummy_parent = OmegaConf.create({}, flags=flags)
    d = {}
    resolved_hints = get_type_hints(get_type_of(obj))
    for field in dataclasses.fields(obj):
        name = field.name
        is_optional, type_ = _resolve_optional(resolved_hints[field.name])
        type_ = _resolve_forward(type_, obj.__module__)

        if hasattr(obj, name):
            value = getattr(obj, name)
            if value == dataclasses.MISSING:
                value = MISSING
        else:
            if field.default_factory == dataclasses.MISSING:  # type: ignore
                value = MISSING
            else:
                value = field.default_factory()  # type: ignore

        if _is_union(type_):
            e = ConfigValueError(
                f"Union types are not supported:\n{name}: {type_str(type_)}"
            )
            format_and_raise(node=None, key=None, value=value, cause=e, msg=str(e))
        d[name] = _maybe_wrap(
            ref_type=type_,
            is_optional=is_optional,
            key=name,
            value=value,
            parent=dummy_parent,
        )
        d[name]._set_parent(None)
    return d