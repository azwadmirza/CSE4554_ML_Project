def status(cwd,
           user=None,
           password=None,
           ignore_retcode=False,
           output_encoding=None):
    '''
    .. versionchanged:: 2015.8.0
        Return data has changed from a list of lists to a dictionary

    Returns the changes to the repository

    cwd
        The path to the git checkout

    user
        User under which to run the git command. By default, the command is run
        by the user under which the minion is running.

    password
        Windows only. Required when specifying ``user``. This parameter will be
        ignored on non-Windows platforms.

      .. versionadded:: 2016.3.4

    ignore_retcode : False
        If ``True``, do not log an error to the minion log if the git command
        returns a nonzero exit status.

        .. versionadded:: 2015.8.0

    output_encoding
        Use this option to specify which encoding to use to decode the output
        from any git commands which are run. This should not be needed in most
        cases.

        .. note::
            This should only be needed if the files in the repository were
            created with filenames using an encoding other than UTF-8 to handle
            Unicode characters.

        .. versionadded:: 2018.3.1

    CLI Example:

    .. code-block:: bash

        salt myminion git.status /path/to/repo
    '''
    cwd = _expand_path(cwd, user)
    state_map = {
        'M': 'modified',
        'A': 'new',
        'D': 'deleted',
        '??': 'untracked'
    }
    ret = {}
    command = ['git', 'status', '-z', '--porcelain']
    output = _git_run(command,
                      cwd=cwd,
                      user=user,
                      password=password,
                      ignore_retcode=ignore_retcode,
                      output_encoding=output_encoding)['stdout']
    for line in output.split('\0'):
        try:
            state, filename = line.split(None, 1)
        except ValueError:
            continue
        ret.setdefault(state_map.get(state, state), []).append(filename)
    return ret