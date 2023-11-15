def _replace_auth_key(
        user,
        key,
        enc='ssh-rsa',
        comment='',
        options=None,
        config='.ssh/authorized_keys'):
    '''
    Replace an existing key
    '''

    auth_line = _format_auth_line(key, enc, comment, options or [])

    lines = []
    full = _get_config_file(user, config)

    try:
        # open the file for both reading AND writing
        with salt.utils.fopen(full, 'r') as _fh:
            for line in _fh:
                if line.startswith('#'):
                    # Commented Line
                    lines.append(line)
                    continue
                comps = re.findall(r'((.*)\s)?(ssh-[a-z0-9-]+|ecdsa-[a-z0-9-]+)\s([a-zA-Z0-9+/]+={0,2})(\s(.*))?', line)
                if comps[0][3] == key:
                    lines.append(auth_line)
                else:
                    lines.append(line)
            _fh.close()
            # Re-open the file writable after properly closing it
            with salt.utils.fopen(full, 'w') as _fh:
                # Write out any changes
                _fh.writelines(lines)
    except (IOError, OSError) as exc:
        raise CommandExecutionError(
            'Problem reading or writing to key file: {0}'.format(exc)
        )