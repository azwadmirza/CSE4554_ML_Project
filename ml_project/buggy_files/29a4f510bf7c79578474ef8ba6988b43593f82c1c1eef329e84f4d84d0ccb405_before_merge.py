def apply_minion_config(overrides=None,
                        defaults=None,
                        cache_minion_id=False,
                        minion_id=None):
    '''
    Returns minion configurations dict.
    '''
    if defaults is None:
        defaults = DEFAULT_MINION_OPTS

    opts = defaults.copy()
    opts['__role'] = 'minion'
    if overrides:
        opts.update(overrides)

    opts['__cli'] = os.path.basename(sys.argv[0])

    # No ID provided. Will getfqdn save us?
    using_ip_for_id = False
    if not opts.get('id'):
        if minion_id:
            opts['id'] = minion_id
        else:
            opts['id'], using_ip_for_id = get_id(
                    opts,
                    cache_minion_id=cache_minion_id)

    # it does not make sense to append a domain to an IP based id
    if not using_ip_for_id and 'append_domain' in opts:
        opts['id'] = _append_domain(opts)

    for directory in opts.get('append_minionid_config_dirs', []):
        if directory in ['pki_dir', 'cachedir', 'extension_modules', 'pidfile']:
            newdirectory = os.path.join(opts[directory], opts['id'])
            opts[directory] = newdirectory

    if len(opts['sock_dir']) > len(opts['cachedir']) + 10:
        opts['sock_dir'] = os.path.join(opts['cachedir'], '.salt-unix')

    # Enabling open mode requires that the value be set to True, and
    # nothing else!
    opts['open_mode'] = opts['open_mode'] is True
    # Make sure ext_mods gets set if it is an untrue value
    # (here to catch older bad configs)
    opts['extension_modules'] = (
        opts.get('extension_modules') or
        os.path.join(opts['cachedir'], 'extmods')
    )
    # Set up the utils_dirs location from the extension_modules location
    opts['utils_dirs'] = (
        opts.get('utils_dirs') or
        [os.path.join(opts['extension_modules'], 'utils')]
    )

    # Insert all 'utils_dirs' directories to the system path
    insert_system_path(opts, opts['utils_dirs'])

    # Prepend root_dir to other paths
    prepend_root_dirs = [
        'pki_dir', 'cachedir', 'sock_dir', 'extension_modules', 'pidfile',
    ]

    # These can be set to syslog, so, not actual paths on the system
    for config_key in ('log_file', 'key_logfile'):
        if urlparse(opts.get(config_key, '')).scheme == '':
            prepend_root_dirs.append(config_key)

    prepend_root_dir(opts, prepend_root_dirs)

    # if there is no beacons option yet, add an empty beacons dict
    if 'beacons' not in opts:
        opts['beacons'] = {}

    if overrides.get('ipc_write_buffer', '') == 'dynamic':
        opts['ipc_write_buffer'] = _DFLT_IPC_WBUFFER
    if 'ipc_write_buffer' not in overrides:
        opts['ipc_write_buffer'] = 0

    # if there is no schedule option yet, add an empty scheduler
    if 'schedule' not in opts:
        opts['schedule'] = {}

    # Make sure hash_type is lowercase
    opts['hash_type'] = opts['hash_type'].lower()

    return opts