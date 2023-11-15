def node_state(id_):
    '''
    Libcloud supported node states
    '''
    states = {0: 'RUNNING',
              1: 'REBOOTING',
              2: 'TERMINATED',
              3: 'PENDING',
              4: 'UNKNOWN',
              5: 'STOPPED',
              6: 'SUSPENDED',
              7: 'ERROR',
              8: 'PAUSED'}
    return states[id_]