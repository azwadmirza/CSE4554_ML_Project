def refresh_modules():
    '''
    Signal the minion to refresh the module and grain data

    CLI Example:

    .. code-block:: bash

        salt '*' saltutil.refresh_modules
    '''
    try:
        ret = __salt__['event.fire']({}, 'module_refresh')
    except Exception as exc:
        log.error('Event module not available. Module refresh failed.')
        ret = False  # Effectively a no-op, since we can't really return without an event system
    return ret