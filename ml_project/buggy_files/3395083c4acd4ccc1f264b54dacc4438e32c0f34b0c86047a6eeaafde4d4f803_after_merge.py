def _available_services(refresh=False):
    '''
    This is a helper function for getting the available macOS services.

    The strategy is to look through the known system locations for
    launchd plist files, parse them, and use their information for
    populating the list of services. Services can run without a plist
    file present, but normally services which have an automated startup
    will have a plist file, so this is a minor compromise.
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
            agent_path = '/Users/{}/Library/LaunchAgents'.format(user)
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
                    if six.PY2:
                        # py2 plistlib can't read binary plists, and
                        # uses a different API than py3.
                        plist = plistlib.readPlist(true_path)
                    else:
                        with salt.utils.files.fopen(true_path, 'rb') as handle:
                            plist = plistlib.load(handle)

                except plistlib.InvalidFileException:
                    # Raised in python3 if the file is not XML.
                    # There's nothing we can do; move on to the next one.
                    msg = 'Unable to parse "%s" as it is invalid XML: InvalidFileException.'
                    logging.warning(msg, true_path)
                    continue

                except xml.parsers.expat.ExpatError:
                    # Raised by py2 for all errors.
                    # Raised by py3 if the file is XML, but with errors.
                    if six.PY3:
                        # There's an error in the XML, so move on.
                        msg = 'Unable to parse "%s" as it is invalid XML: xml.parsers.expat.ExpatError.'
                        logging.warning(msg, true_path)
                        continue

                    # Use the system provided plutil program to attempt
                    # conversion from binary.
                    cmd = '/usr/bin/plutil -convert xml1 -o - -- "{0}"'.format(
                        true_path)
                    try:
                        plist_xml = __salt__['cmd.run'](cmd)
                        plist = plistlib.readPlistFromString(plist_xml)
                    except xml.parsers.expat.ExpatError:
                        # There's still an error in the XML, so move on.
                        msg = 'Unable to parse "%s" as it is invalid XML: xml.parsers.expat.ExpatError.'
                        logging.warning(msg, true_path)
                        continue

                _available_services[plist['Label'].lower()] = {
                    'file_name': file_name,
                    'file_path': true_path,
                    'plist': plist}

    # put this in __context__ as this is a time consuming function.
    # a fix for this issue. https://github.com/saltstack/salt/issues/48414
    __context__['available_services'] = _available_services
    # this is a fresh gathering of services, set cached to false
    __context__['using_cached_services'] = False

    return __context__['available_services']