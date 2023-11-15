def gemset_present(name, ruby='default', runas=None, user=None):
    '''
    Verify that the gemset is present.

    name
        The name of the gemset.

    ruby: default
        The ruby version this gemset belongs to.

    runas: None
        The user to run rvm as.

        .. deprecated:: 0.17.0

    user: None
        The user to run rvm as.

        .. versionadded:: 0.17.0
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    salt.utils.warn_until(
        'Hydrogen',
        'Please remove \'runas\' support at this stage. \'user\' support was '
        'added in 0.17.0',
        _dont_call_warnings=True
    )
    if runas:
        # Warn users about the deprecation
        ret.setdefault('warnings', []).append(
            'The \'runas\' argument is being deprecated in favor or \'user\', '
            'please update your state files.'
        )
    if user is not None and runas is not None:
        # user wins over runas but let warn about the deprecation.
        ret.setdefault('warnings', []).append(
            'Passed both the \'runas\' and \'user\' arguments. Please don\'t. '
            '\'runas\' is being ignored in favor of \'user\'.'
        )
        runas = None
    elif runas is not None:
        # Support old runas usage
        user = runas
        runas = None

    ret = _check_rvm(ret, user)
    if ret['result'] is False:
        return ret

    if '@' in name:
        ruby, name = name.split('@')
        ret = _check_ruby(ret, ruby)
        if not ret['result']:
            ret['result'] = False
            ret['comment'] = 'Requested ruby implementation was not found.'
            return ret

    if name in __salt__['rvm.gemset_list'](ruby, runas=user):
        ret['result'] = True
        ret['comment'] = 'Gemset already exists.'
    else:
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Set to install gemset {0}'.format(name)
            return ret
        if __salt__['rvm.gemset_create'](ruby, name, runas=user):
            ret['result'] = True
            ret['comment'] = 'Gemset successfully created.'
            ret['changes'][name] = 'created'
        else:
            ret['result'] = False
            ret['comment'] = 'Gemset could not be created.'

    return ret