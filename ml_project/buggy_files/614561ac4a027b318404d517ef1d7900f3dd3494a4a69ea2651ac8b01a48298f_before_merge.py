def refresh_pillar():
    '''
    Signal the minion to refresh the pillar data.

    CLI Example:

    .. code-block:: bash

        salt '*' saltutil.refresh_pillar
    '''
    return __salt__['event.fire']({}, 'pillar_refresh')