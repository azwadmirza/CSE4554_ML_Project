def get_permissions(obj_name, principal=None, obj_type='file'):
    '''
    Get the permissions for the passed object

    Args:

        obj_name (str): The name of or path to the object.

        principal (Optional[str]): The name of the user or group for which to
        get permissions. Can also pass a SID. If None, all ACEs defined on the
        object will be returned. Default is None

        obj_type (Optional[str]): The type of object for which to get
        permissions.

    Returns:
        dict: A dictionary representing the object permissions

    Usage:

    .. code-block:: python

        salt.utils.win_dacl.get_permissions('C:\\Temp')
    '''
    obj_dacl = dacl(obj_name, obj_type)

    if principal is None:
        return obj_dacl.list_aces()

    return obj_dacl.get_ace(principal)