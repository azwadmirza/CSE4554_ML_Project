def _sysv_enabled(name):
    '''
    A System-V style service is assumed disabled if the "startup" symlink
    (starts with "S") to its script is found in /etc/init.d in the current
    runlevel.
    '''
    return bool(glob.glob('/etc/rc%s.d/S*%s' % (_runlevel(), name)))