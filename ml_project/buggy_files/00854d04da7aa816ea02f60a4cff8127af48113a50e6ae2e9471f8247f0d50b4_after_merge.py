def format_sql(sql, params):
    # type: (Any, Any) -> Tuple[str, List[str]]
    rv = []

    if isinstance(params, dict):
        # convert sql with named parameters to sql with unnamed parameters
        conv = _FormatConverter(params)
        if params:
            sql = sql % conv
            params = conv.params
        else:
            params = ()

    for param in params or ():
        if param is None:
            rv.append("NULL")
        param = safe_repr(param)
        rv.append(param)

    return sql, rv