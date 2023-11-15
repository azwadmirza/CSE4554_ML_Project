def get_inheritance(obj_name, obj_type='file'):
    '''
    Get an object's inheritance.

    Args:

        obj_name (str): The name of the object

        obj_type (Optional[str]): The type of object. Only three object types
        allow inheritance. Valid objects are:

            - file (default): This is a file or directory
            - registry
            - registry32 (for WOW64)

            The following should return False as there is no inheritance:

            - service
            - printer
            - share

    Returns:
        bool: True if enabled, otherwise False

    Usage:

    .. code-block:: python

        salt.utils.win_dacl.get_inheritance('HKLM\\SOFTWARE\\salt', 'registry')
    '''
    dacl = Dacl(obj_name, obj_type)
    inherited = win32security.INHERITED_ACE

    for i in range(0, dacl.dacl.GetAceCount()):
        ace = dacl.dacl.GetAce(i)
        if ace[0][1] & inherited == inherited:
            return True

    return False