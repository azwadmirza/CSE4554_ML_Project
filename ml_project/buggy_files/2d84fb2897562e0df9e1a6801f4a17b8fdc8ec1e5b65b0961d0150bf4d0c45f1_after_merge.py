def parse_level(line, dest):
    level_group = ('emergencies', 'alerts', 'critical', 'errors', 'warning',
                   'notifications', 'informational', 'debugging')

    if dest == 'hostnameprefix':
        level = 'debugging'

    else:
        match = re.search(r'logging {} (\S+)'.format(dest), line, re.M)
        if match:
            if match.group(1) in level_group:
                level = match.group(1)
            else:
                level = 'debugging'
        else:
            level = 'debugging'

    return level