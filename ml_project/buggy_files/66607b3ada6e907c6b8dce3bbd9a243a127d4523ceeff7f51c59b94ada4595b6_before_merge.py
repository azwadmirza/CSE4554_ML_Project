def present(name, bare=True, runas=None, user=None, force=False):
    '''
    Make sure the repository is present in the given directory

    name
        Name of the directory where the repository is about to be created

    bare
        Create a bare repository (Default: True)

    runas
        Name of the user performing repository management operations

        .. deprecated:: 0.17.0

    user
        Name of the user performing repository management operations

        .. versionadded:: 0.17.0

    force
        Force-create a new repository into an pre-existing non-git directory
        (deletes contents)
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    salt.utils.warn_until(
        (0, 18),
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

    # If the named directory is a git repo return True
    if os.path.isdir(name):
        if bare and os.path.isfile('{0}/HEAD'.format(name)):
            return ret
        elif not bare and os.path.isdir('{0}/.git'.format(name)):
            return ret
        # Directory exists and is not a git repo, if force is set destroy the
        # directory and recreate, otherwise throw an error
        elif not force and os.listdir(name):
            return _fail(ret,
                         'Directory which does not contain a git repo '
                         'is already present at {0}. To delete this '
                         'directory and create a fresh git repo set '
                         'force: True'.format(name))

    # Run test is set
    if __opts__['test']:
        ret['changes']['new repository'] = name
        return _neutral_test(ret, ('New git repo set for'
                                   ' creation at {0}').format(name))

    if force and os.path.isdir(name):
        if os.path.islink(name):
            os.remove(name)
        else:
            shutil.rmtree(name)

    opts = '--bare' if bare else ''
    __salt__['git.init'](cwd=name, user=user, opts=opts)

    message = 'Initialized repository {0}'.format(name)
    log.info(message)
    ret['changes']['new repository'] = name
    ret['comment'] = message

    return ret