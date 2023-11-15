def _override_attr(
    sub_node: str, data_class: Type[FairseqDataclass], args: Namespace
) -> List[str]:
    overrides = []

    if not inspect.isclass(data_class) or not issubclass(data_class, FairseqDataclass):
        return overrides

    def get_default(f):
        if not isinstance(f.default_factory, _MISSING_TYPE):
            return f.default_factory()
        return f.default

    for k, v in data_class.__dataclass_fields__.items():
        if k.startswith("_"):
            # private member, skip
            continue

        val = get_default(v) if not hasattr(args, k) else getattr(args, k)

        if getattr(v.type, "__origin__", None) is List:
            # if type is int but val is float, then we will crash later - try to convert here
            t_args = v.type.__args__
            if len(t_args) == 1:
                val = list(map(t_args[0], val))

        if val is None:
            overrides.append("{}.{}=null".format(sub_node, k))
        elif val == "":
            overrides.append("{}.{}=''".format(sub_node, k))
        elif isinstance(val, str):
            overrides.append("{}.{}='{}'".format(sub_node, k, val))
        else:
            overrides.append("{}.{}={}".format(sub_node, k, val))
    return overrides