def exists(name):
    '''
    Returns whether the named container exists.

    .. code-block:: bash

        salt '*' lxc.exists name
    '''
    l = list_()
    return name in (l['running'] + l['stopped'] + l['frozen'])