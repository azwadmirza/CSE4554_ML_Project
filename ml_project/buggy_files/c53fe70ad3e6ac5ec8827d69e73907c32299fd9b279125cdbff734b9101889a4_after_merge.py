def _cpv_to_cp(cpv):
    try:
        ret = portage.dep_getkey(cpv)
        if ret:
            return ret
    except portage.exception.InvalidAtom:
        pass

    return cpv