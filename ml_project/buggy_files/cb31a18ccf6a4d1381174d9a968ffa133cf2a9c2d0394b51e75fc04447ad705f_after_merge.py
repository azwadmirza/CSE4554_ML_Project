def summarize_coord(name, var, col_width):
    is_index = name in var.dims
    show_values = is_index or _not_remote(var)
    marker = u'*' if is_index else u' '
    return _summarize_var_or_coord(name, var, col_width, show_values, marker)