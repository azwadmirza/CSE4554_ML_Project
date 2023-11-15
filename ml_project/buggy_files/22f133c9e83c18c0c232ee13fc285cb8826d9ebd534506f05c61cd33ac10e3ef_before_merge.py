def _summarize_var_or_coord(name, var, col_width, show_values=True,
                            marker=' ', max_width=None):
    if max_width is None:
        max_width = OPTIONS['display_width']
    first_col = pretty_print('  %s %s ' % (marker, name), col_width)
    dims_str = '(%s) ' % ', '.join(map(str, var.dims)) if var.dims else ''
    front_str = first_col + dims_str + ('%s ' % var.dtype)
    if show_values:
        values_str = format_array_flat(var, max_width - len(front_str))
    else:
        values_str = '...'
    return front_str + values_str