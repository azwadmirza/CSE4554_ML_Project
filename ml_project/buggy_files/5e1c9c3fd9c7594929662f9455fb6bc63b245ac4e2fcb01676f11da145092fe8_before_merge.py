def _format_option_value(optdict, value):
    """return the user input's value from a 'compiled' value"""
    if isinstance(value, (list, tuple)):
        value = ','.join(value)
    elif isinstance(value, dict):
        value = ','.join('%s:%s' % (k, v) for k, v in value.items())
    elif hasattr(value, 'match'): # optdict.get('type') == 'regexp'
        # compiled regexp
        value = value.pattern
    elif optdict.get('type') == 'yn':
        value = value and 'yes' or 'no'
    elif isinstance(value, six.string_types) and value.isspace():
        value = "'%s'" % value
    return value