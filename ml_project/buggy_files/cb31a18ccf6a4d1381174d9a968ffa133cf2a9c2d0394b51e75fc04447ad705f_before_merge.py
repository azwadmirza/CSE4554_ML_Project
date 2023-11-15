def summarize_coord(name, var, col_width):
    is_index = name in var.dims
    show_values = is_index or _not_remote(var)
    marker = '*' if is_index else ' '
    return _summarize_var_or_coord(name, var, col_width, show_values, marker)