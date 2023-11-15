def _summarize_var_or_coord(name, var, col_width, show_values=True,
                            marker=' ', max_width=None):
    if max_width is None:
        max_width = OPTIONS['display_width']
    first_col = pretty_print(u'  %s %s ' % (marker, name), col_width)
    if var.dims:
        dims_str = u'(%s) ' % u', '.join(map(unicode_type, var.dims))
    else:
        dims_str = u''
    front_str = u'%s%s%s ' % (first_col, dims_str, var.dtype)
    if show_values:
        values_str = format_array_flat(var, max_width - len(front_str))
    else:
        values_str = u'...'
    return front_str + values_str