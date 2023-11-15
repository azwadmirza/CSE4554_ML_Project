def output(ret, **kwargs):
    '''
    Display ret data
    '''
    # Prefer kwargs before opts
    retcode = kwargs.get('_retcode', 0)
    base_indent = kwargs.get('nested_indent', 0) \
        or __opts__.get('nested_indent', 0)
    nest = NestDisplay(retcode=retcode)
    return '\n'.join(nest.display(ret, base_indent, '', []))