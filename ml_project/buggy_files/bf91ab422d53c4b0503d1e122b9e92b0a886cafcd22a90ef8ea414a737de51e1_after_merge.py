def highstate(test=None, queue=False, **kwargs):
    '''
    Retrieve the state data from the salt master for this minion and execute it

    CLI Example:

    .. code-block:: bash

        salt '*' state.highstate

        salt '*' state.highstate exclude=sls_to_exclude
        salt '*' state.highstate exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"
    '''
    if queue:
        _wait(kwargs['__pub_jid'])
    else:
        conflict = running()
        if conflict:
            __context__['retcode'] = 1
            return conflict
    opts = copy.copy(__opts__)

    if salt.utils.test_mode(test=test, **kwargs):
        opts['test'] = True
    else:
        opts['test'] = __opts__.get('test', None)

    if 'env' in kwargs:
        opts['environment'] = kwargs['env']

    pillar = kwargs.get('pillar')

    st_ = salt.state.HighState(opts, pillar, kwargs.get('__pub_jid'))
    st_.push_active()
    try:
        ret = st_.call_highstate(
                exclude=kwargs.get('exclude', []),
                cache=kwargs.get('cache', None),
                cache_name=kwargs.get('cache_name', 'highstate'),
                force=kwargs.get('force', False)
                )
    finally:
        st_.pop_active()

    if __salt__['config.option']('state_data', '') == 'terse' or \
            kwargs.get('terse'):
        ret = _filter_running(ret)
    serial = salt.payload.Serial(__opts__)
    cache_file = os.path.join(__opts__['cachedir'], 'highstate.p')

    # Not 100% if this should be fatal or not,
    # but I'm guessing it likely should not be.
    cumask = os.umask(191)
    try:
        if salt.utils.is_windows():
            # Make sure cache file isn't read-only
            __salt__['cmd.run']('attrib -R "{0}"'.format(cache_file))
        with salt.utils.fopen(cache_file, 'w+') as fp_:
            serial.dump(ret, fp_)
    except (IOError, OSError):
        msg = 'Unable to write to "state.highstate" cache file {0}'
        log.error(msg.format(cache_file))
    os.umask(cumask)
    _set_retcode(ret)
    return ret