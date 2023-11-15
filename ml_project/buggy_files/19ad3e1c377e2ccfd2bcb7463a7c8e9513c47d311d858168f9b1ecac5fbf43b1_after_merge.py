def _available_services():
    '''
    This is a helper function needed for testing. We are using the memoziation
    decorator on the `available_services` function, which causes the function
    to run once and then return the results of the first run on subsequent
    calls. This causes problems when trying to test the functionality of the
    `available_services` function.
    '''
    launchd_paths = [
        '/Library/LaunchAgents',
        '/Library/LaunchDaemons',
        '/System/Library/LaunchAgents',
        '/System/Library/LaunchDaemons',
    ]
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
                    plist = plistlib.readPlist(true_path)

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

    return _available_services