def _p_to_cp(p):
    '''
    Convert a package name or a DEPEND atom to category/package format.
    Raises an exception if program name is ambiguous.
    '''
    try:
        ret = portage.dep_getkey(p)
        if ret:
            return ret
    except portage.exception.InvalidAtom:
        pass

    try:
        ret = _porttree().dbapi.xmatch('bestmatch-visible', p)
        if ret:
            return portage.dep_getkey(ret)
    except portage.exception.InvalidAtom:
        pass

    return None