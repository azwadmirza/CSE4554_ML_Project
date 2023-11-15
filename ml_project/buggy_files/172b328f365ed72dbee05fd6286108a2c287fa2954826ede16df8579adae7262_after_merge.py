def sls(mods, test=None, exclude=None, queue=False, sync_mods=None, **kwargs):
    '''
    Execute the states in one or more SLS files

    test
        Run states in test-only (dry-run) mode

    pillar
        Custom Pillar values, passed as a dictionary of key-value pairs

        .. code-block:: bash

            salt '*' state.apply test pillar='{"foo": "bar"}'

        .. note::
            Values passed this way will override Pillar values set via
            ``pillar_roots`` or an external Pillar source.

        .. versionchanged:: 2016.3.0
            GPG-encrypted CLI Pillar data is now supported via the GPG
            renderer. See :ref:`here <encrypted-cli-pillar-data>` for details.

    pillar_enc
        Specify which renderer to use to decrypt encrypted data located within
        the ``pillar`` value. Currently, only ``gpg`` is supported.

        .. versionadded:: 2016.3.0

    exclude
        Exclude specific states from execution. Accepts a list of sls names, a
        comma-separated string of sls names, or a list of dictionaries
        containing ``sls`` or ``id`` keys. Glob-patterns may be used to match
        multiple states.

        .. code-block:: bash

            salt '*' state.sls foo,bar,baz exclude=bar,baz
            salt '*' state.sls foo,bar,baz exclude=ba*
            salt '*' state.sls foo,bar,baz exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"

    queue : False
        Instead of failing immediately when another state run is in progress,
        queue the new state run to begin running once the other has finished.

        This option starts a new thread for each queued state run, so use this
        option sparingly.

    concurrent : False
        Execute state runs concurrently instead of serially

        .. warning::

            This flag is potentially dangerous. It is designed for use when
            multiple state runs can safely be run at the same time. Do *not*
            use this flag for performance optimization.

    saltenv
        Specify a salt fileserver environment to be used when applying states

        .. versionchanged:: 0.17.0
            Argument name changed from ``env`` to ``saltenv``.

        .. versionchanged:: 2014.7.0
            If no saltenv is specified, the minion config will be checked for an
            ``environment`` parameter and if found, it will be used. If none is
            found, ``base`` will be used. In prior releases, the minion config
            was not checked and ``base`` would always be assumed when the
            saltenv was not explicitly set.

    pillarenv
        Specify a Pillar environment to be used when applying states. This
        can also be set in the minion config file using the
        :conf_minion:`pillarenv` option. When neither the
        :conf_minion:`pillarenv` minion config option nor this CLI argument is
        used, all Pillar environments will be merged together.

    localconfig

        Optionally, instead of using the minion config, load minion opts from
        the file specified by this argument, and then merge them with the
        options from the minion config. This functionality allows for specific
        states to be run with their own custom minion configuration, including
        different pillars, file_roots, etc.

    mock:
        The mock option allows for the state run to execute without actually
        calling any states. This then returns a mocked return which will show
        the requisite ordering as well as fully validate the state run.

        .. versionadded:: 2015.8.4

    sync_mods
        If specified, the desired custom module types will be synced prior to
        running the SLS files:

        .. code-block:: bash

            salt '*' state.sls test sync_mods=states,modules
            salt '*' state.sls test sync_mods=all

        .. versionadded:: 2017.7.8,2018.3.3,Fluorine

    CLI Example:

    .. code-block:: bash

        salt '*' state.sls core,edit.vim dev
        salt '*' state.sls core exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"

        salt '*' state.sls myslsfile pillar="{foo: 'Foo!', bar: 'Bar!'}"
    '''
    concurrent = kwargs.get('concurrent', False)
    if 'env' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'Parameter \'env\' has been detected in the argument list.  This '
            'parameter is no longer used and has been replaced by \'saltenv\' '
            'as of Salt 2016.11.0.  This warning will be removed in Salt Oxygen.'
            )
        kwargs.pop('env')

    # Modification to __opts__ lost after this if-else
    if queue:
        _wait(kwargs.get('__pub_jid'))
    else:
        conflict = running(concurrent)
        if conflict:
            __context__['retcode'] = 1
            return conflict

    if isinstance(mods, list):
        disabled = _disabled(mods)
    else:
        disabled = _disabled([mods])

    if disabled:
        for state in disabled:
            log.debug(
                'Salt state %s is disabled. To re-enable, run '
                'state.enable %s', state, state
            )
        __context__['retcode'] = 1
        return disabled

    orig_test = __opts__.get('test', None)
    opts = _get_opts(**kwargs)

    opts['test'] = _get_test_value(test, **kwargs)

    # Since this is running a specific SLS file (or files), fall back to the
    # 'base' saltenv if none is configured and none was passed.
    if opts['environment'] is None:
        opts['environment'] = 'base'

    pillar_override = kwargs.get('pillar')
    pillar_enc = kwargs.get('pillar_enc')
    if pillar_enc is None \
            and pillar_override is not None \
            and not isinstance(pillar_override, dict):
        raise SaltInvocationError(
            'Pillar data must be formatted as a dictionary, unless pillar_enc '
            'is specified.'
        )

    serial = salt.payload.Serial(__opts__)
    cfn = os.path.join(
            __opts__['cachedir'],
            '{0}.cache.p'.format(kwargs.get('cache_name', 'highstate'))
            )

    if sync_mods is True:
        sync_mods = ['all']
    if sync_mods is not None:
        sync_mods = salt.utils.split_input(sync_mods)
    else:
        sync_mods = []

    if 'all' in sync_mods and sync_mods != ['all']:
        # Prevent unnecessary extra syncing
        sync_mods = ['all']

    for module_type in sync_mods:
        try:
            __salt__['saltutil.sync_{0}'.format(module_type)](
                saltenv=opts['environment']
            )
        except KeyError:
            log.warning(
                'Invalid custom module type \'%s\', ignoring',
                module_type
            )

    try:
        st_ = salt.state.HighState(opts,
                                   pillar_override,
                                   kwargs.get('__pub_jid'),
                                   pillar_enc=pillar_enc,
                                   proxy=__proxy__,
                                   context=__context__,
                                   mocked=kwargs.get('mock', False),
                                   initial_pillar=_get_initial_pillar(opts))
    except NameError:
        st_ = salt.state.HighState(opts,
                                   pillar_override,
                                   kwargs.get('__pub_jid'),
                                   pillar_enc=pillar_enc,
                                   mocked=kwargs.get('mock', False),
                                   initial_pillar=_get_initial_pillar(opts))

    errors = _get_pillar_errors(kwargs, pillar=st_.opts['pillar'])
    if errors:
        __context__['retcode'] = 5
        return ['Pillar failed to render with the following messages:'] + errors

    orchestration_jid = kwargs.get('orchestration_jid')
    with salt.utils.files.set_umask(0o077):
        if kwargs.get('cache'):
            if os.path.isfile(cfn):
                with salt.utils.fopen(cfn, 'rb') as fp_:
                    high_ = serial.load(fp_)
                    return st_.state.call_high(high_, orchestration_jid)

    if isinstance(mods, six.string_types):
        mods = mods.split(',')

    st_.push_active()
    try:
        high_, errors = st_.render_highstate({opts['environment']: mods})

        if errors:
            __context__['retcode'] = 1
            return errors

        if exclude:
            if isinstance(exclude, str):
                exclude = exclude.split(',')
            if '__exclude__' in high_:
                high_['__exclude__'].extend(exclude)
            else:
                high_['__exclude__'] = exclude
        snapper_pre = _snapper_pre(opts, kwargs.get('__pub_jid', 'called localy'))
        ret = st_.state.call_high(high_, orchestration_jid)
    finally:
        st_.pop_active()
    if __salt__['config.option']('state_data', '') == 'terse' or kwargs.get('terse'):
        ret = _filter_running(ret)
    cache_file = os.path.join(__opts__['cachedir'], 'sls.p')
    with salt.utils.files.set_umask(0o077):
        try:
            if salt.utils.is_windows():
                # Make sure cache file isn't read-only
                __salt__['cmd.run'](['attrib', '-R', cache_file], python_shell=False)
            with salt.utils.fopen(cache_file, 'w+b') as fp_:
                serial.dump(ret, fp_)
        except (IOError, OSError):
            msg = 'Unable to write to SLS cache file {0}. Check permission.'
            log.error(msg.format(cache_file))
        _set_retcode(ret, high_)
        # Work around Windows multiprocessing bug, set __opts__['test'] back to
        # value from before this function was run.
        __opts__['test'] = orig_test

        try:
            with salt.utils.fopen(cfn, 'w+b') as fp_:
                try:
                    serial.dump(high_, fp_)
                except TypeError:
                    # Can't serialize pydsl
                    pass
        except (IOError, OSError):
            msg = 'Unable to write to highstate cache file {0}. Do you have permissions?'
            log.error(msg.format(cfn))

    _snapper_post(opts, kwargs.get('__pub_jid', 'called localy'), snapper_pre)
    return ret