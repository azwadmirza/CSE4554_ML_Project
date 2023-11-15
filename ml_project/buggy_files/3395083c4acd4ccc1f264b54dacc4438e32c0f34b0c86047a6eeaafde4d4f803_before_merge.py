def _available_services(refresh=False):
    '''
    This is a helper function for getting the available macOS services.
    '''
    try:
        if __context__['available_services'] and not refresh:
            log.debug('Found context for available services.')
            __context__['using_cached_services'] = True
            return __context__['available_services']
    except KeyError:
        pass

    launchd_paths = [
        '/Library/LaunchAgents',
        '/Library/LaunchDaemons',
        '/System/Library/LaunchAgents',
        '/System/Library/LaunchDaemons',
    ]

    try:
        for user in os.listdir('/Users/'):
            agent_path = '/Users/{}/Library/LaunchAgents/'.format(user)
            if os.path.isdir(agent_path):
                launchd_paths.append(agent_path)
    except OSError:
        pass

    _available_services = dict()
    for launch_dir in launchd_paths:
        for root, dirs, files in salt.utils.path.os_walk(launch_dir):
            for file_name in files:

                # Must be a plist file
                if not file_name.endswith('.plist'):
                    continue

                # Follow symbolic links of files in _launchd_paths
                file_path = os.path.join(root, file_name)
                true_path = os.path.realpath(file_path)

                # ignore broken symlinks
                if not os.path.exists(true_path):
                    continue

                try:
                    # This assumes most of the plist files
                    # will be already in XML format
                    if six.PY2:
                        plist = plistlib.readPlist(true_path)
                    else:
                        with salt.utils.files.fopen(true_path, 'rb') as plist_handle:
                            plist = plistlib.load(plist_handle)

                except Exception:
                    # If plistlib is unable to read the file we'll need to use
                    # the system provided plutil program to do the conversion
                    cmd = '/usr/bin/plutil -convert xml1 -o - -- "{0}"'.format(
                        true_path)
                    plist_xml = __salt__['cmd.run'](cmd)
                    if six.PY2:
                        plist = plistlib.readPlistFromString(plist_xml)
                    else:
                        plist = plistlib.loads(
                            salt.utils.stringutils.to_bytes(plist_xml))

                try:
                    _available_services[plist.Label.lower()] = {
                        'file_name': file_name,
                        'file_path': true_path,
                        'plist': plist}
                except AttributeError:
                    # Handle malformed plist files
                    _available_services[os.path.basename(file_name).lower()] = {
                        'file_name': file_name,
                        'file_path': true_path,
                        'plist': plist}

    # put this in __context__ as this is a time consuming function.
    # a fix for this issue. https://github.com/saltstack/salt/issues/48414
    __context__['available_services'] = _available_services
    # this is a fresh gathering of services, set cached to false
    __context__['using_cached_services'] = False

    return __context__['available_services']