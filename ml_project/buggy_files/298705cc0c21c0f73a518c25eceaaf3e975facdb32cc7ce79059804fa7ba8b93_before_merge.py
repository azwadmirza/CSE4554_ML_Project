def refresh_modules():
    '''
    Signal the minion to refresh the module and grain data

    CLI Example:

    .. code-block:: bash

        salt '*' saltutil.refresh_modules
    '''
    return __salt__['event.fire']({}, 'module_refresh')