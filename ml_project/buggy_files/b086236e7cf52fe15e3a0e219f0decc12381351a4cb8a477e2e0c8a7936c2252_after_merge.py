def node_state(id_):
    '''
    Libcloud supported node states
    '''
    states_int = {
        0: 'RUNNING',
        1: 'REBOOTING',
        2: 'TERMINATED',
        3: 'PENDING',
        4: 'UNKNOWN',
        5: 'STOPPED',
        6: 'SUSPENDED',
        7: 'ERROR',
        8: 'PAUSED'}
    states_str = {
        'running': 'RUNNING',
        'rebooting': 'REBOOTING',
        'starting': 'STARTING',
        'terminated': 'TERMINATED',
        'pending': 'PENDING',
        'unknown': 'UNKNOWN',
        'stopping': 'STOPPING',
        'stopped': 'STOPPED',
        'suspended': 'SUSPENDED',
        'error': 'ERROR',
        'paused': 'PAUSED',
        'reconfiguring': 'RECONFIGURING'
    }
    return states_str[id_] if isinstance(id_, string_types) else states_int[id_]