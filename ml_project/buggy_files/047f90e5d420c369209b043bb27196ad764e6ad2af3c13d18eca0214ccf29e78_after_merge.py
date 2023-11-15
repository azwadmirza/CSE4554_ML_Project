def global_max(col_vals, index):
    """Returns the global maximum and minimum"""
    col_vals_without_None = [x for x in col_vals if x is not None]
    max_col, min_col = zip(*col_vals_without_None)
    return max(max_col), min(min_col)