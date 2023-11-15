def init(cwd,
         bare=False,
         template=None,
         separate_git_dir=None,
         shared=None,
         opts='',
         user=None,
         ignore_retcode=False):
    '''
    Interface to `git-init(1)`_

    cwd
        The path to the directory to be initialized

    bare : False
        If ``True``, init a bare repository

        .. versionadded:: 2015.8.0

    template
        Set this argument to specify an alternate `template directory`_

        .. versionadded:: 2015.8.0

    separate_git_dir
        Set this argument to specify an alternate ``$GIT_DIR``

        .. versionadded:: 2015.8.0

    shared
        Set sharing permissions on git repo. See `git-init(1)`_ for more
        details.

        .. versionadded:: 2015.8.0

    opts
        Any additional options to add to the command line, in a single string

        .. note::
            On the Salt CLI, if the opts are preceded with a dash, it is
            necessary to precede them with ``opts=`` (as in the CLI examples
            below) to avoid causing errors with Salt's own argument parsing.

    user
        User under which to run the git command. By default, the command is run
        by the user under which the minion is running.

    ignore_retcode : False
        If ``True``, do not log an error to the minion log if the git command
        returns a nonzero exit status.

        .. versionadded:: 2015.8.0

    .. _`git-init(1)`: http://git-scm.com/docs/git-init
    .. _`template directory`: http://git-scm.com/docs/git-init#_template_directory


    CLI Examples:

    .. code-block:: bash

        salt myminion git.init /path/to/repo
        # Init a bare repo (before 2015.8.0)
        salt myminion git.init /path/to/bare/repo.git opts='--bare'
        # Init a bare repo (2015.8.0 and later)
        salt myminion git.init /path/to/bare/repo.git bare=True
    '''
    cwd = _expand_path(cwd, user)
    command = ['git', 'init']
    if bare:
        command.append('--bare')
    if template is not None:
        if not isinstance(template, six.string_types):
            template = str(template)
        command.append('--template={0}'.format(template))
    if separate_git_dir is not None:
        if not isinstance(separate_git_dir, six.string_types):
            separate_git_dir = str(separate_git_dir)
        command.append('--separate-git-dir={0}'.format(separate_git_dir))
    if shared is not None:
        if isinstance(shared, six.integer_types):
            shared = '0' + str(shared)
        elif not isinstance(shared, six.string_types):
            # Using lower here because booleans would be capitalized when
            # converted to a string.
            shared = str(shared).lower()
        command.append('--shared={0}'.format(shared))
    command.extend(_format_opts(opts))
    command.append(cwd)
    return _git_run(command,
                    runas=user,
                    ignore_retcode=ignore_retcode)['stdout']