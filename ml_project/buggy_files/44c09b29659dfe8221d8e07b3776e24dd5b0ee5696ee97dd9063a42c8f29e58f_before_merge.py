def set_permissions(obj_name,
                    principal,
                    permissions,
                    access_mode='grant',
                    applies_to='this_folder_subfolders_files',
                    obj_type='file',
                    reset_perms=False,
                    protected=None):
    '''
    Set the permissions of an object. This can be a file, folder, registry key,
    printer, service, etc...

    Args:

        obj_name (str): The object for which to set permissions. This can be the
        path to a file or folder, a registry key, printer, etc. For more
        information about how to format the name see:

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa379593(v=vs.85).aspx


        principal (str): The name of the user or group for which to set
        permissions. Can also pass a SID.

        permissions (str, list): The type of permissions to grant/deny the user.
        Can be one of the basic permissions, or a list of advanced permissions.

        access_mode (Optional[str]): Whether to grant or deny user the access.
        Valid options are:

            - grant (default): Grants the user access
            - deny: Denies the user access

        applies_to (Optional[str]): The objects to which these permissions will
        apply. Not all these options apply to all object types. Defaults to
        'this_folder_subfolders_files'

        obj_type (Optional[str]): The type of object for which to set
        permissions. Default is 'file'

        reset_perms (Optional[bool]): True will overwrite the permissions on the
        specified object. False will append the permissions. Default is False

        protected (Optional[bool]): True will disable inheritance for the
        object. False will enable inheritance. None will make no change. Default
        is None.

    Returns:
        bool: True if successful, raises an error otherwise

    Usage:

    .. code-block:: python

        salt.utils.win_dacl.set_permissions(
            'C:\\Temp', 'jsnuffy', 'full_control', 'grant')
    '''
    # If you don't pass `obj_name` it will create a blank DACL
    # Otherwise, it will grab the existing DACL and add to it
    if reset_perms:
        dacl = Dacl(obj_type=obj_type)
    else:
        dacl = Dacl(obj_name, obj_type)
        dacl.rm_ace(principal, access_mode)

    dacl.add_ace(principal, access_mode, permissions, applies_to)

    dacl.order_acl()

    dacl.save(obj_name, protected)

    return True