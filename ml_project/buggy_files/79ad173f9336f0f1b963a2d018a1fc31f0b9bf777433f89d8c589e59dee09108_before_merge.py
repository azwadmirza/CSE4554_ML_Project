def broadcast_change():
    '''
    Refresh the windows environment.

    Returns (bool): True if successful, otherwise False

    CLI Example:

    .. code-block:: bash

        salt '*' reg.broadcast_change
    '''
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms644952(v=vs.85).aspx
    _, res = SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0,
                                SMTO_ABORTIFHUNG, 5000)
    return not bool(res)