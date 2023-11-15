def format_item(x, timedelta_format=None, quote_strings=True):
    """Returns a succinct summary of an object as a string"""
    if isinstance(x, (np.datetime64, datetime)):
        return format_timestamp(x)
    if isinstance(x, (np.timedelta64, timedelta)):
        return format_timedelta(x, timedelta_format=timedelta_format)
    elif isinstance(x, (unicode_type, bytes_type)):
        return repr(x) if quote_strings else x
    elif isinstance(x, (float, np.float)):
        return '{0:.4}'.format(x)
    else:
        return str(x)