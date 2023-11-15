def win_verify_env(dirs, permissive=False, pki_dir='', skip_extra=False):
    '''
    Verify that the named directories are in place and that the environment
    can shake the salt
    '''
    import salt.utils.win_functions
    import salt.utils.win_dacl

    # Get the root path directory where salt is installed
    path = dirs[0]
    while os.path.basename(path) not in ['salt', 'salt-tests-tmpdir']:
        path, base = os.path.split(path)

    # Create the root path directory if missing
    if not os.path.isdir(path):
        os.makedirs(path)

    # Set permissions to the root path directory
    current_user = salt.utils.win_functions.get_current_user()
    if salt.utils.win_functions.is_admin(current_user):
        try:
            # Make the Administrators group owner
            # Use the SID to be locale agnostic
            salt.utils.win_dacl.set_owner(path, 'S-1-5-32-544')

        except CommandExecutionError:
            msg = 'Unable to securely set the owner of "{0}".'.format(path)
            if is_console_configured():
                log.critical(msg)
            else:
                sys.stderr.write("CRITICAL: {0}\n".format(msg))

        if not permissive:
            try:
                # Get a clean dacl by not passing an obj_name
                dacl = salt.utils.win_dacl.Dacl()

                # Add aces to the dacl, use the GUID (locale non-specific)
                # Administrators Group
                dacl.add_ace('S-1-5-32-544', 'grant', 'full_control',
                             'this_folder_subfolders_files')
                # System
                dacl.add_ace('S-1-5-18', 'grant', 'full_control',
                             'this_folder_subfolders_files')
                # Owner
                dacl.add_ace('S-1-3-4', 'grant', 'full_control',
                             'this_folder_subfolders_files')

                # Save the dacl to the object
                dacl.save(path, True)

            except CommandExecutionError:
                msg = 'Unable to securely set the permissions of ' \
                      '"{0}".'.format(path)
                if is_console_configured():
                    log.critical(msg)
                else:
                    sys.stderr.write("CRITICAL: {0}\n".format(msg))

    # Create the directories
    for dir_ in dirs:
        if not dir_:
            continue
        if not os.path.isdir(dir_):
            try:
                os.makedirs(dir_)
            except OSError as err:
                msg = 'Failed to create directory path "{0}" - {1}\n'
                sys.stderr.write(msg.format(dir_, err))
                sys.exit(err.errno)

        # The PKI dir gets its own permissions
        if dir_ == pki_dir:
            try:
                # Make Administrators group the owner
                salt.utils.win_dacl.set_owner(path, 'S-1-5-32-544')

                # Give Admins, System and Owner permissions
                # Get a clean dacl by not passing an obj_name
                dacl = salt.utils.win_dacl.Dacl()

                # Add aces to the dacl, use the GUID (locale non-specific)
                # Administrators Group
                dacl.add_ace('S-1-5-32-544', 'grant', 'full_control',
                             'this_folder_subfolders_files')
                # System
                dacl.add_ace('S-1-5-18', 'grant', 'full_control',
                             'this_folder_subfolders_files')
                # Owner
                dacl.add_ace('S-1-3-4', 'grant', 'full_control',
                             'this_folder_subfolders_files')

                # Save the dacl to the object
                dacl.save(dir_, True)

            except CommandExecutionError:
                msg = 'Unable to securely set the permissions of "{0}".'
                msg = msg.format(dir_)
                if is_console_configured():
                    log.critical(msg)
                else:
                    sys.stderr.write("CRITICAL: {0}\n".format(msg))

    if skip_extra is False:
        # Run the extra verification checks
        zmq_version()