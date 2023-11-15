def _regex_to_static(src, regex):
    '''
    Expand regular expression to static match.
    '''
    if not src or not regex:
        return None

    try:
        src = re.search(regex, src)
    except Exception as ex:
        raise CommandExecutionError("{0}: '{1}'".format(_get_error_message(ex), regex))

    return src and src.group() or regex