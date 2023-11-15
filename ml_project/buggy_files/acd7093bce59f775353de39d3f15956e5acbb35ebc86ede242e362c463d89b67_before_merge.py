def apply_master_config(overrides=None, defaults=None):
    '''
    Returns master configurations dict.
    '''
    import salt.crypt
    if defaults is None:
        defaults = DEFAULT_MASTER_OPTS

    opts = defaults.copy()
    opts['__role'] = 'master'
    if overrides:
        opts.update(overrides)

    opts['__cli'] = os.path.basename(sys.argv[0])

    if len(opts['sock_dir']) > len(opts['cachedir']) + 10:
        opts['sock_dir'] = os.path.join(opts['cachedir'], '.salt-unix')

    opts['extension_modules'] = (
        opts.get('extension_modules') or
        os.path.join(opts['cachedir'], 'extmods')
    )
    opts['token_dir'] = os.path.join(opts['cachedir'], 'tokens')
    opts['syndic_dir'] = os.path.join(opts['cachedir'], 'syndics')
    if (overrides or {}).get('ipc_write_buffer', '') == 'dynamic':
        opts['ipc_write_buffer'] = _DFLT_IPC_WBUFFER
    if 'ipc_write_buffer' not in overrides:
        opts['ipc_write_buffer'] = 0
    using_ip_for_id = False
    append_master = False
    if not opts.get('id'):
        opts['id'], using_ip_for_id = get_id(
                opts,
                cache_minion_id=None)
        append_master = True

    # it does not make sense to append a domain to an IP based id
    if not using_ip_for_id and 'append_domain' in opts:
        opts['id'] = _append_domain(opts)
    if append_master:
        opts['id'] += '_master'

    # Prepend root_dir to other paths
    prepend_root_dirs = [
        'pki_dir', 'cachedir', 'pidfile', 'sock_dir', 'extension_modules',
        'autosign_file', 'autoreject_file', 'token_dir', 'syndic_dir',
        'sqlite_queue_dir'
    ]

    # These can be set to syslog, so, not actual paths on the system
    for config_key in ('log_file', 'key_logfile', 'ssh_log_file'):
        log_setting = opts.get(config_key, '')
        if log_setting is None:
            continue

        if urlparse(log_setting).scheme == '':
            prepend_root_dirs.append(config_key)

    prepend_root_dir(opts, prepend_root_dirs)

    # Enabling open mode requires that the value be set to True, and
    # nothing else!
    opts['open_mode'] = opts['open_mode'] is True
    opts['auto_accept'] = opts['auto_accept'] is True
    opts['file_roots'] = _validate_file_roots(opts['file_roots'])
    opts['pillar_roots'] = _validate_file_roots(opts['pillar_roots'])

    if opts['file_ignore_regex']:
        # If file_ignore_regex was given, make sure it's wrapped in a list.
        # Only keep valid regex entries for improved performance later on.
        if isinstance(opts['file_ignore_regex'], str):
            ignore_regex = [opts['file_ignore_regex']]
        elif isinstance(opts['file_ignore_regex'], list):
            ignore_regex = opts['file_ignore_regex']

        opts['file_ignore_regex'] = []
        for regex in ignore_regex:
            try:
                # Can't store compiled regex itself in opts (breaks
                # serialization)
                re.compile(regex)
                opts['file_ignore_regex'].append(regex)
            except Exception:
                log.warning(
                    'Unable to parse file_ignore_regex. Skipping: {0}'.format(
                        regex
                    )
                )

    if opts['file_ignore_glob']:
        # If file_ignore_glob was given, make sure it's wrapped in a list.
        if isinstance(opts['file_ignore_glob'], str):
            opts['file_ignore_glob'] = [opts['file_ignore_glob']]

    # Let's make sure `worker_threads` does not drop below 3 which has proven
    # to make `salt.modules.publish` not work under the test-suite.
    if opts['worker_threads'] < 3 and opts.get('peer', None):
        log.warning(
            "The 'worker_threads' setting on '{0}' cannot be lower than "
            '3. Resetting it to the default value of 3.'.format(
                opts['conf_file']
            )
        )
        opts['worker_threads'] = 3

    opts.setdefault('pillar_source_merging_strategy', 'smart')

    # Make sure hash_type is lowercase
    opts['hash_type'] = opts['hash_type'].lower()

    # Check and update TLS/SSL configuration
    _update_ssl_config(opts)

    return opts