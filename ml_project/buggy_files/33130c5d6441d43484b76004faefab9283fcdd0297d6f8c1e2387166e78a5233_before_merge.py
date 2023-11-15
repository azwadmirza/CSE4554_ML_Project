def rm_permissions(obj_name,
                   principal,
                   ace_type='all',
                   obj_type='file'):
    r'''
    Remove a user's ACE from an object. This can be a file, folder, registry
    key, printer, service, etc...

    Args:

        obj_name (str): The object from which to remove the ace. This can be the
        path to a file or folder, a registry key, printer, etc. For more
        information about how to format the name see:

        https://msdn.microsoft.com/en-us/library/windows/desktop/aa379593(v=vs.85).aspx

        principal (str): The name of the user or group for which to set
        permissions. Can also pass a SID.

        ace_type(Optional[str]): The type of ace to remove. There are two types
        of ACEs, 'grant' and 'deny'. 'all' will remove all ACEs for the user.
        Default is 'all'

        obj_type (Optional[str]): The type of object for which to set
        permissions. Default is 'file'

    Returns:
        bool: True if successful, raises an error otherwise

    Usage:

    .. code-block:: python

        # Remove jsnuffy's grant ACE from C:\Temp
        salt.utils.win_dacl.rm_permissions('C:\\Temp', 'jsnuffy', 'grant')

        # Remove all ACEs for jsnuffy from C:\Temp
        salt.utils.win_dacl.rm_permissions('C:\\Temp', 'jsnuffy')
    '''
    dacl = Dacl(obj_name, obj_type)

    dacl.rm_ace(principal, ace_type)
    dacl.save(obj_name)

    return True