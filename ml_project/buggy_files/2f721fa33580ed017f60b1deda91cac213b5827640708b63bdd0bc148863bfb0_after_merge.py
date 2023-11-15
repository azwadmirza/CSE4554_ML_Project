def has_permission(obj_name,
                   principal,
                   permission,
                   access_mode='grant',
                   obj_type='file',
                   exact=True):
    r'''
    Check if the object has a permission

    Args:

        obj_name (str): The name of or path to the object.

        principal (str): The name of the user or group for which to get
        permissions. Can also pass a SID.

        permission (str): The permission to verify. Valid options depend on the
        obj_type.

        access_mode (Optional[str]): The access mode to check. Is the user
        granted or denied the permission. Default is 'grant'. Valid options are:

            - grant
            - deny

        obj_type (Optional[str]): The type of object for which to check
        permissions. Default is 'file'

        exact (Optional[bool]): True for an exact match, otherwise check to see
        if the permission is included in the ACE. Default is True

    Returns:
        bool: True if the object has the permission, otherwise False

    Usage:

    .. code-block:: python

        # Does Joe have read permissions to C:\Temp
        salt.utils.win_dacl.has_permission(
            'C:\\Temp', 'joe', 'read', 'grant', False)

        # Does Joe have Full Control of C:\Temp
        salt.utils.win_dacl.has_permission(
            'C:\\Temp', 'joe', 'full_control', 'grant')
    '''
    # Validate access_mode
    if access_mode.lower() not in ['grant', 'deny']:
        raise SaltInvocationError(
            'Invalid "access_mode" passed: {0}'.format(access_mode))
    access_mode = access_mode.lower()

    # Get the DACL
    obj_dacl = dacl(obj_name, obj_type)

    obj_type = obj_type.lower()

    # Get a PySID object
    sid = get_sid(principal)

    # Get the passed permission flag, check basic first
    chk_flag = obj_dacl.ace_perms[obj_type]['basic'].get(
        permission.lower(),
        obj_dacl.ace_perms[obj_type]['advanced'].get(permission.lower(), False))
    if not chk_flag:
        raise SaltInvocationError(
            'Invalid "permission" passed: {0}'.format(permission))

    # Check each ace for sid and type
    cur_flag = None
    for i in range(0, obj_dacl.dacl.GetAceCount()):
        ace = obj_dacl.dacl.GetAce(i)
        if ace[2] == sid and obj_dacl.ace_type[ace[0][0]] == access_mode:
            cur_flag = ace[1]

    # If the ace is empty, return false
    if not cur_flag:
        return False

    # Check for the exact permission in the ACE
    if exact:
        return chk_flag == cur_flag

    # Check if the ACE contains the permission
    return cur_flag & chk_flag == chk_flag