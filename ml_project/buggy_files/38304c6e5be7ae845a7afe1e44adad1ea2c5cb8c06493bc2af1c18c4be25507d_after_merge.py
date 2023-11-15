def apply_minion_config(overrides=None,
                        defaults=None,
                        check_dns=None,
                        minion_id=False):
    '''
    Returns minion configurations dict.
    '''
    if check_dns is not None:
        # All use of the `check_dns` arg was removed in `598d715`. The keyword
        # argument was then removed in `9d893e4` and `**kwargs` was then added
        # in `5d60f77` in order not to break backwards compatibility.
        #
        # Showing a deprecation for 0.17.0 and 0.18.0 should be enough for any
        # api calls to be updated in order to stop it's use.
        salt.utils.warn_until(
            'Helium',
            'The functionality behind the \'check_dns\' keyword argument is '
            'no longer required, as such, it became unnecessary and is now '
            'deprecated. \'check_dns\' will be removed in Salt {version}.'
        )

    if defaults is None:
        defaults = DEFAULT_MINION_OPTS

    opts = defaults.copy()
    if overrides:
        opts.update(overrides)

    if len(opts['sock_dir']) > len(opts['cachedir']) + 10:
        opts['sock_dir'] = os.path.join(opts['cachedir'], '.salt-unix')

    # No ID provided. Will getfqdn save us?
    using_ip_for_id = False
    if opts['id'] is None and minion_id:
        opts['id'], using_ip_for_id = get_id(opts['root_dir'])

    # it does not make sense to append a domain to an IP based id
    if not using_ip_for_id and 'append_domain' in opts:
        opts['id'] = _append_domain(opts)

    # Enabling open mode requires that the value be set to True, and
    # nothing else!
    opts['open_mode'] = opts['open_mode'] is True

    # set up the extension_modules location from the cachedir
    opts['extension_modules'] = (
        opts.get('extension_modules') or
        os.path.join(opts['cachedir'], 'extmods')
    )

    # Prepend root_dir to other paths
    prepend_root_dirs = [
        'pki_dir', 'cachedir', 'sock_dir', 'extension_modules', 'pidfile',
    ]

    # These can be set to syslog, so, not actual paths on the system
    for config_key in ('log_file', 'key_logfile'):
        if urlparse.urlparse(opts.get(config_key, '')).scheme == '':
            prepend_root_dirs.append(config_key)

    prepend_root_dir(opts, prepend_root_dirs)
    if '__mine_interval' not in opts.get('schedule', {}):
        if not 'schedule' in opts:
            opts['schedule'] = {}
        opts['schedule'].update({
            '__mine_interval':
            {
                'function': 'mine.update',
                'minutes': opts['mine_interval']
            }
        })
    return opts