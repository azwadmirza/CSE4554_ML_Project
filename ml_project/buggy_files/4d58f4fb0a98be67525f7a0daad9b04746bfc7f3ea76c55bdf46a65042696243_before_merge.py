def highstate(test=None, queue=False, **kwargs):
    '''
    Retrieve the state data from the salt master for this minion and execute it

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

    queue : False
        Instead of failing immediately when another state run is in progress,
        queue the new state run to begin running once the other has finished.

        This option starts a new thread for each queued state run, so use this
        option sparingly.

    localconfig
        Optionally, instead of using the minion config, load minion opts from
        the file specified by this argument, and then merge them with the
        options from the minion config. This functionality allows for specific
        states to be run with their own custom minion configuration, including
        different pillars, file_roots, etc.

    mock
        The mock option allows for the state run to execute without actually
        calling any states. This then returns a mocked return which will show
        the requisite ordering as well as fully validate the state run.

        .. versionadded:: 2015.8.4

    CLI Examples:

    .. code-block:: bash

        salt '*' state.highstate

        salt '*' state.highstate whitelist=sls1_to_run,sls2_to_run
        salt '*' state.highstate exclude=sls_to_exclude
        salt '*' state.highstate exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"

        salt '*' state.highstate pillar="{foo: 'Foo!', bar: 'Bar!'}"
    '''
    if _disabled(['highstate']):
        log.debug('Salt highstate run is disabled. To re-enable, run state.enable highstate')
        ret = {
            'name': 'Salt highstate run is disabled. To re-enable, run state.enable highstate',
            'result': 'False',
            'comment': 'Disabled'
        }
        return ret

    conflict = _check_queue(queue, kwargs)
    if conflict is not None:
        return conflict
    orig_test = __opts__.get('test', None)

    opts = _get_opts(**kwargs)

    opts['test'] = _get_test_value(test, **kwargs)

    if 'env' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'Parameter \'env\' has been detected in the argument list.  This '
            'parameter is no longer used and has been replaced by \'saltenv\' '
            'as of Salt 2016.11.0.  This warning will be removed in Salt Oxygen.'
            )
        kwargs.pop('env')

    pillar_override = kwargs.get('pillar')
    pillar_enc = kwargs.get('pillar_enc')
    if pillar_enc is None \
            and pillar_override is not None \
            and not isinstance(pillar_override, dict):
        raise SaltInvocationError(
            'Pillar data must be formatted as a dictionary, unless pillar_enc '
            'is specified.'
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

    if not _check_pillar(kwargs, st_.opts['pillar']):
        __context__['retcode'] = 5
        err = ['Pillar failed to render with the following messages:']
        err += __pillar__['_errors']
        return err

    st_.push_active()
    ret = {}
    orchestration_jid = kwargs.get('orchestration_jid')
    snapper_pre = _snapper_pre(opts, kwargs.get('__pub_jid', 'called localy'))
    try:
        ret = st_.call_highstate(
                exclude=kwargs.get('exclude', []),
                cache=kwargs.get('cache', None),
                cache_name=kwargs.get('cache_name', 'highstate'),
                force=kwargs.get('force', False),
                whitelist=kwargs.get('whitelist'),
                orchestration_jid=orchestration_jid)
    finally:
        st_.pop_active()

    if __salt__['config.option']('state_data', '') == 'terse' or \
            kwargs.get('terse'):
        ret = _filter_running(ret)

    serial = salt.payload.Serial(__opts__)
    cache_file = os.path.join(__opts__['cachedir'], 'highstate.p')
    _set_retcode(ret)
    # Work around Windows multiprocessing bug, set __opts__['test'] back to
    # value from before this function was run.
    _snapper_post(opts, kwargs.get('__pub_jid', 'called localy'), snapper_pre)
    __opts__['test'] = orig_test
    return ret