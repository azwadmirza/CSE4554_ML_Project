def _filter_names(
    names: Iterable,
    label: str,
    include: Optional[Iterable],
    exclude: Optional[Iterable],
):
    if include and exclude:
        intersection = set(include) & set(exclude)
        if intersection:
            values = ", ".join(intersection)
            raise InvalidArgumentError(
                f"'{values}' specified in both --include-{label} and"
                f" --exclude-{label}"
            )

    names = [tuple(name.split(".")) for name in names]

    def _filter(filters, update_func):
        filters = [tuple(name.split(".")) for name in filters]
        for length, groups in groupby(filters, len):
            for group in groups:
                matches = [name for name in names if name[:length] == group]
                if not matches:
                    name = ".".join(group)
                    raise InvalidArgumentError(
                        f"'{name}' does not match any known {label}"
                    )
                update_func({match: None for match in matches})

    if include:
        ret: OrderedDict = OrderedDict()
        _filter(include, ret.update)
    else:
        ret = OrderedDict({name: None for name in names})

    if exclude:
        _filter(exclude, ret.difference_update)  # type: ignore[attr-defined]

    return [".".join(name) for name in ret]