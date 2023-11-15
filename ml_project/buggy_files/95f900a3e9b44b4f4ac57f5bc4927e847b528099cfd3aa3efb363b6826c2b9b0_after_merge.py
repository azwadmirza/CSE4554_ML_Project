def summarize_attr(key, value, col_width=None):
    # ignore col_width for now to more clearly distinguish attributes
    return u'    %s: %s' % (key, maybe_truncate(value))