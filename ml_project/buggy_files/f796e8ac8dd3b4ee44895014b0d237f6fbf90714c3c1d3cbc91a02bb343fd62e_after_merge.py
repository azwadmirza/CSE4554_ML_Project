def _sysv_enabled(name):
    '''
    A System-V style service is assumed disabled if the "startup" symlink
    (starts with "S") to its script is found in /etc/init.d in the current
    runlevel.
    '''
    # Find exact match (disambiguate matches like "S01anacron" for cron)
    for match in glob.glob('/etc/rc%s.d/S*%s' % (_runlevel(), name)):
        if re.match(r'S\d{,2}%s' % name, os.path.basename(match)):
            return True
    return False