def format_float_locale(value, format=".2f"):
    """Turn a float into a grouped, locale-dependent string
    e.g. 12345.67 -> "12,345.67" or "12.345,67" etc"""
    return locale.format(format, value, grouping=True)