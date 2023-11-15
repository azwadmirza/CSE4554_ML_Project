def absent(name, runas=None, user=None):
    '''
    Verify that the specified ruby is not installed with rbenv. Rbenv
    is installed if necessary.

    name
        The version of ruby to uninstall

    runas: None
        The user to run rbenv as.

        .. deprecated:: 0.17.0

    user: None
        The user to run rbenv as.

        .. versionadded:: 0.17.0

    .. versionadded:: 0.16.0
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

    if name.startswith('ruby-'):
        name = re.sub(r'^ruby-', '', name)

    if __opts__['test']:
        ret['comment'] = 'Ruby {0} is set to be uninstalled'.format(name)
        return ret

    ret = _check_rbenv(ret, user)
    if ret['result'] is False:
        ret['result'] = True
        ret['comment'] = 'Rbenv not installed, {0} not either'.format(name)
        return ret
    else:
        return _check_and_uninstall_ruby(ret, name, user=user)