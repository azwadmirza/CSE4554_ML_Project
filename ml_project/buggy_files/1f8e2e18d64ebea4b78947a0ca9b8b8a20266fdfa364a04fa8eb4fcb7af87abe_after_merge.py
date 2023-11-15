def _calculate_col_width(mapping):
    max_name_length = (max(len(unicode_type(k)) for k in mapping)
                       if mapping else 0)
    col_width = max(max_name_length, 7) + 6
    return col_width