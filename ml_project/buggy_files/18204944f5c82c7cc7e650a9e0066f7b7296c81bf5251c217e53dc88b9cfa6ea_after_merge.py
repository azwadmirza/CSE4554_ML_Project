def output(ret, **kwargs):
    '''
    Display ret data
    '''
    # Prefer kwargs before opts
    retcode = kwargs.get('_retcode', 0)
    base_indent = kwargs.get('nested_indent', 0) \
        or __opts__.get('nested_indent', 0)
    nest = NestDisplay(retcode=retcode)
    lines = nest.display(ret, base_indent, '', [])
    try:
        return '\n'.join(lines)
    except UnicodeDecodeError:
        # output contains binary data that can't be decoded
        return str('\n').join(  # future lint: disable=blacklisted-function
            [salt.utils.stringutils.to_str(x) for x in lines]
        )