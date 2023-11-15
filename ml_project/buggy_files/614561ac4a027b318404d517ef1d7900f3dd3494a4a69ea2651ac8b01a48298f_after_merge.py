def refresh_pillar():
    '''
    Signal the minion to refresh the pillar data.

    CLI Example:

    .. code-block:: bash

        salt '*' saltutil.refresh_pillar
    '''
    try:
        ret = __salt__['event.fire']({}, 'pillar_refresh')
    except Exception as exc:
        log.error('Event module not available. Module refresh failed.')
        ret = False  # Effectively a no-op, since we can't really return without an event system
    return ret