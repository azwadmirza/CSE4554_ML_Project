def remove_values(value, no_log_strings):
    """ Remove strings in no_log_strings from value.  If value is a container
    type, then remove a lot more"""
    if isinstance(value, basestring):
        if isinstance(value, unicode):
            # This should work everywhere on python2. Need to check
            # surrogateescape on python3
            bytes_value = value.encode('utf-8')
            value_is_unicode = True
        else:
            bytes_value = value
            value_is_unicode = False
        if bytes_value in no_log_strings:
            return 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'
        for omit_me in no_log_strings:
            bytes_value = bytes_value.replace(omit_me, '*' * 8)
        if value_is_unicode:
            value = unicode(bytes_value, 'utf-8', errors='replace')
        else:
            value = bytes_value
    elif isinstance(value, Sequence):
        return [remove_values(elem, no_log_strings) for elem in value]
    elif isinstance(value, Mapping):
        return dict((k, remove_values(v, no_log_strings)) for k, v in value.items())
    elif isinstance(value, tuple(chain(NUMBERTYPES, (bool, NoneType)))):
        stringy_value = str(value)
        if stringy_value in no_log_strings:
            return 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'
        for omit_me in no_log_strings:
            if omit_me in stringy_value:
                return 'VALUE_SPECIFIED_IN_NO_LOG_PARAMETER'
    else:
        raise TypeError('Value of unknown type: %s, %s' % (type(value), value))
    return value