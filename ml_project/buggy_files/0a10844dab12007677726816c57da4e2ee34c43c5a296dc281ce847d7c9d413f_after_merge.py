def set_inheritance(obj_name, enabled, obj_type='file', clear=False):
    '''
    Enable or disable an objects inheritance.

    Args:

        obj_name (str): The name of the object

        enabled (bool): True to enable inheritance, False to disable

        obj_type (Optional[str]): The type of object. Only three objects allow
        inheritance. Valid objects are:

            - file (default): This is a file or directory
            - registry
            - registry32 (for WOW64)

        clear (Optional[bool]): True to clear existing ACEs, False to keep
        existing ACEs. Default is False

    Returns:
        bool: True if successful, otherwise an Error

    Usage:

    .. code-block:: python

        salt.utils.win_dacl.set_inheritance('C:\\Temp', False)
    '''
    if obj_type not in ['file', 'registry', 'registry32']:
        raise SaltInvocationError(
            'obj_type called with incorrect parameter: {0}'.format(obj_name))

    if clear:
        obj_dacl = dacl(obj_type=obj_type)
    else:
        obj_dacl = dacl(obj_name, obj_type)

    return obj_dacl.save(obj_name, not enabled)