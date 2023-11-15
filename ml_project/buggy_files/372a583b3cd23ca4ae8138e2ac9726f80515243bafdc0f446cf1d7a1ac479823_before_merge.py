def execute_touch(path, follow):
    b_path = to_bytes(path, errors='surrogate_or_strict')
    prev_state = get_state(b_path)

    if not module.check_mode:
        if prev_state == 'absent':
            # Create an empty file if the filename did not already exist
            try:
                open(b_path, 'wb').close()
            except (OSError, IOError) as e:
                raise AnsibleModuleError(results={'msg': 'Error, could not touch target: %s'
                                                         % to_native(e, nonstring='simplerepr'),
                                                  'path': path})

        elif prev_state in ('file', 'directory', 'hard'):
            # Update the timestamp if the file already existed
            try:
                os.utime(b_path, None)
            except OSError as e:
                raise AnsibleModuleError(results={'msg': 'Error while touching existing target: %s'
                                                         % to_native(e, nonstring='simplerepr'),
                                                  'path': path})

        elif prev_state == 'link' and follow:
            # Update the timestamp of the pointed to file
            b_link_target = os.readlink(b_path)
            try:
                os.utime(b_link_target, None)
            except OSError as e:
                raise AnsibleModuleError(results={'msg': 'Error while touching existing target: %s'
                                                         % to_native(e, nonstring='simplerepr'),
                                                  'path': path})

        else:
            raise AnsibleModuleError(results={'msg': 'Can only touch files, directories, and'
                                                     ' hardlinks (%s is %s)' % (path, prev_state)})

        # Update the attributes on the file
        diff = initial_diff(path, 'touch', prev_state)
        file_args = module.load_file_common_arguments(module.params)
        try:
            module.set_fs_attributes_if_different(file_args, True, diff, expand=False)
        except SystemExit as e:
            if e.code:
                # We take this to mean that fail_json() was called from
                # somewhere in basic.py
                if prev_state == 'absent':
                    # If we just created the file we can safely remove it
                    os.remove(b_path)
            raise

    # Unfortunately, touch always changes the file because it updates file's timestamp
    return {'dest': path, 'changed': True, 'diff': diff}