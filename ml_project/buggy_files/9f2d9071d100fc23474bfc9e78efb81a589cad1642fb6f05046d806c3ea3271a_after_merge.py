def diskusage(human_readable=False, path=None):
    '''
    .. versionadded:: 2015.8.0

    Return the disk usage for this minion

    human_readable : False
        If ``True``, usage will be in KB/MB/GB etc.

    CLI Example:

    .. code-block:: bash

        salt '*' status.diskusage path=c:/salt
    '''
    if not path:
        path = 'c:/'

    # Credit for the source and ideas for this function:
    # http://code.activestate.com/recipes/577972-disk-usage/?in=user-4178764
    _, total, free = \
        ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_longlong()
    if sys.version_info >= (3, ) or isinstance(path, six.text_type):
        fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
    else:
        fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
    ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
    if ret == 0:
        raise ctypes.WinError()
    used = total.value - free.value

    total_val = total.value
    used_val = used
    free_val = free.value

    if human_readable:
        total_val = _byte_calc(total_val)
        used_val = _byte_calc(used_val)
        free_val = _byte_calc(free_val)

    return {'total': total_val, 'used': used_val, 'free': free_val}