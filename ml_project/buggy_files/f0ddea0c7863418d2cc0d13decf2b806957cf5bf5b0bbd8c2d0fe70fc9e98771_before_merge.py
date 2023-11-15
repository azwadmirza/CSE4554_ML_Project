def format_int_locale(value):
    """Turn an integer into a grouped, locale-dependent string
    e.g. 12345 -> "12,345" or "12.345" etc"""
    return locale.format("%d", value, grouping=True)