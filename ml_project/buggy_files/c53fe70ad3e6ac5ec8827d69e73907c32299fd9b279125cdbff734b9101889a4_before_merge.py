def _cpv_to_cp(cpv):
    ret = portage.cpv_getkey(cpv)
    if ret:
        return ret
    else:
        return cpv