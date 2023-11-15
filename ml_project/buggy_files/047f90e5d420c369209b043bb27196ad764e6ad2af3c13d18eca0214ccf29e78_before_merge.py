def global_max(col_vals, index):
    """Returns the global maximum and minimum"""
    max_col, min_col = zip(*col_vals)
    return max(max_col), min(min_col)