def __virtual__():
    '''
    Virtual service only on systems using runit as init process (PID 1).
    Otherwise, use this module with the provider mechanism.
    '''
    if __grains__.get('init') == 'runit':
        if __grains__['os'] == 'Void':
            add_svc_avail_path('/etc/sv')
        return __virtualname__
    return False