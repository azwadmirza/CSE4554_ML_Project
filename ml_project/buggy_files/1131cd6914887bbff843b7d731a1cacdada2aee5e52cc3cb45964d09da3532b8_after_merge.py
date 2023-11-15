def destroy(name, stop=True):
    '''
    Destroy the named container.
    WARNING: Destroys all data associated with the container.

    .. code-block:: bash

        salt '*' lxc.destroy name [stop=(true|false)]
    '''
    if stop:
        _change_state('lxc-stop', name, 'stopped')
    return _change_state('lxc-destroy', name, None)