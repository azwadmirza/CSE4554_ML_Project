def destroy(name):
    '''
    Destroy the named container.
    WARNING: Destroys all data associated with the container.

    .. code-block:: bash

        salt '*' lxc.destroy name
    '''
    return _change_state('lxc-destroy', name, None)