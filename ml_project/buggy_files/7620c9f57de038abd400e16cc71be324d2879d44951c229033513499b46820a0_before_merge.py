def sls(mods, env='base', test=None, exclude=None, queue=False, **kwargs):
    '''
    Execute a set list of state modules from an environment, default
    environment is base

    CLI Example:

    .. code-block:: bash

        salt '*' state.sls core,edit.vim dev
        salt '*' state.sls core exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"
    '''

    if queue:
        _wait(kwargs['__pub_jid'])
    else:
        conflict = running()
        if conflict:
            __context__['retcode'] = 1
            return conflict
    if not _check_pillar(kwargs):
        __context__['retcode'] = 5
        err = ['Pillar failed to render with the following messages:']
        err += __pillar__['_errors']
        return err
    opts = copy.copy(__opts__)

    if salt.utils.test_mode(test=test, **kwargs):
        opts['test'] = True
    else:
        opts['test'] = __opts__.get('test', None)

    pillar = kwargs.get('pillar')

    serial = salt.payload.Serial(__opts__)
    cfn = os.path.join(
            __opts__['cachedir'],
            '{0}.cache.p'.format(kwargs.get('cache_name', 'highstate'))
            )

    st_ = salt.state.HighState(opts, pillar, kwargs.get('__pub_jid'))

    if kwargs.get('cache'):
        if os.path.isfile(cfn):
            with salt.utils.fopen(cfn, 'r') as fp_:
                high_ = serial.load(fp_)
                return st_.state.call_high(high_)

    if isinstance(mods, string_types):
        mods = mods.split(',')

    st_.push_active()
    try:
        high_, errors = st_.render_highstate({env: mods})

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
        ret = st_.state.call_high(high_)
    finally:
        st_.pop_active()
    if __salt__['config.option']('state_data', '') == 'terse' or kwargs.get('terse'):
        ret = _filter_running(ret)
    cache_file = os.path.join(__opts__['cachedir'], 'sls.p')
    cumask = os.umask(191)
    try:
        with salt.utils.fopen(cache_file, 'w+') as fp_:
            serial.dump(ret, fp_)
    except (IOError, OSError):
        msg = 'Unable to write to "state.sls" cache file {0}'
        log.error(msg.format(cache_file))
    os.umask(cumask)
    _set_retcode(ret)
    with salt.utils.fopen(cfn, 'w+') as fp_:
        try:
            serial.dump(high_, fp_)
        except TypeError:
            # Can't serialize pydsl
            pass
    return ret