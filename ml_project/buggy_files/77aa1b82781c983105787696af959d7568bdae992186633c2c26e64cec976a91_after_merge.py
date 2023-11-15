def _clean_na_values(na_values, keep_default_na=True):

    if na_values is None:
        if keep_default_na:
            na_values = _NA_VALUES
        else:
            na_values = set()
        na_fvalues = set()
    elif isinstance(na_values, dict):
        na_values = na_values.copy()  # Prevent aliasing.
        if keep_default_na:
            for k, v in compat.iteritems(na_values):
                if not is_list_like(v):
                    v = [v]
                v = set(v) | _NA_VALUES
                na_values[k] = v
        na_fvalues = dict([
            (k, _floatify_na_values(v)) for k, v in na_values.items()  # noqa
        ])
    else:
        if not is_list_like(na_values):
            na_values = [na_values]
        na_values = _stringify_na_values(na_values)
        if keep_default_na:
            na_values = na_values | _NA_VALUES

        na_fvalues = _floatify_na_values(na_values)

    return na_values, na_fvalues