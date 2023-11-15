def _p_to_cp(p):
    '''
    Convert a package name or a DEPEND atom to category/package format.
    Raises an exception if program name is ambiguous.
    '''
    ret = _porttree().dbapi.xmatch("match-all", p)
    if ret:
        return portage.cpv_getkey(ret[0])
    return None