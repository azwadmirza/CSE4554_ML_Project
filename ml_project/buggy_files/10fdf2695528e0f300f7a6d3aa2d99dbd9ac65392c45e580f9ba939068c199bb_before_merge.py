def set_owner(obj_name, principal, obj_type='file'):
    '''
    Set the owner of an object. This can be a file, folder, registry key,
    printer, service, etc...

    Args:

        obj_name (str): The object for which to set owner. This can be the path
        to a file or folder, a registry key, printer, etc. For more information
        about how to format the name see:

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa379593(v=vs.85).aspx

        principal (str): The name of the user or group to make owner of the
        object. Can also pass a SID.

        obj_type (Optional[str]): The type of object for which to set the owner.

    Returns:
        bool: True if successful, raises an error otherwise

    Usage:

    .. code-block:: python

        salt.utils.win_dacl.set_owner('C:\\MyDirectory', 'jsnuffy', 'file')
    '''
    sid = get_sid(principal)

    flags = Flags()

    # To set the owner to something other than the logged in user requires
    # SE_TAKE_OWNERSHIP_NAME and SE_RESTORE_NAME privileges
    # Enable them for the logged in user
    # Setup the privilege set
    new_privs = set()
    luid = win32security.LookupPrivilegeValue('', 'SeTakeOwnershipPrivilege')
    new_privs.add((luid, win32con.SE_PRIVILEGE_ENABLED))
    luid = win32security.LookupPrivilegeValue('', 'SeRestorePrivilege')
    new_privs.add((luid, win32con.SE_PRIVILEGE_ENABLED))

    # Get the current token
    p_handle = win32api.GetCurrentProcess()
    t_handle = win32security.OpenProcessToken(
        p_handle,
        win32security.TOKEN_ALL_ACCESS | win32con.TOKEN_ADJUST_PRIVILEGES)

    # Enable the privileges
    win32security.AdjustTokenPrivileges(t_handle, 0, new_privs)

    # Set the user
    try:
        win32security.SetNamedSecurityInfo(
            obj_name,
            flags.obj_type[obj_type],
            flags.element['owner'],
            sid,
            None, None, None)
    except pywintypes.error as exc:
        log.debug('Failed to make {0} the owner: {1}'.format(principal, exc[2]))
        raise CommandExecutionError(
            'Failed to set owner: {0}'.format(exc[2]))

    return True