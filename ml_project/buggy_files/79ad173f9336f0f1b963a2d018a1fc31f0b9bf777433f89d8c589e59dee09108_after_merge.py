def broadcast_change():
    '''
    Refresh the windows environment.

    Returns (bool): True if successful, otherwise False

    CLI Example:

    .. code-block:: bash

        salt '*' reg.broadcast_change
    '''
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms644952(v=vs.85).aspx
    _, res = win32gui.SendMessageTimeout(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 0,
        win32con.SMTO_ABORTIFHUNG, 5000)
    return not bool(res)