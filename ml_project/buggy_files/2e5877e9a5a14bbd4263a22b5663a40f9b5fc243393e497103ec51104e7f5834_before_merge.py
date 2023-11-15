def refresh_db(**kwargs):
    '''
    Fetches metadata files and calls :py:func:`pkg.genrepo
    <salt.modules.win_pkg.genrepo>` to compile updated repository metadata.

    Kwargs:

        saltenv (str): Salt environment. Default: ``base``

        verbose (bool):
            Return verbose data structure which includes 'success_list', a list
            of all sls files and the package names contained within. Default
            'False'

        failhard (bool):
            If ``True``, an error will be raised if any repo SLS files failed to
            process. If ``False``, no error will be raised, and a dictionary
            containing the full results will be returned.

    Returns:
        dict: A dictionary containing the results of the database refresh.

    .. Warning::
        When calling this command from a state using `module.run` be sure to
        pass `failhard: False`. Otherwise the state will report failure if it
        encounters a bad software definition file.

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.refresh_db
        salt '*' pkg.refresh_db saltenv=base
    '''
    # Remove rtag file to keep multiple refreshes from happening in pkg states
    salt.utils.pkg.clear_rtag(__opts__)
    saltenv = kwargs.pop('saltenv', 'base')
    verbose = salt.utils.is_true(kwargs.pop('verbose', False))
    failhard = salt.utils.is_true(kwargs.pop('failhard', True))
    __context__.pop('winrepo.data', None)
    repo_details = _get_repo_details(saltenv)

    log.debug(
        'Refreshing pkg metadata db for saltenv \'%s\' (age of existing '
        'metadata is %s)',
        saltenv, datetime.timedelta(seconds=repo_details.winrepo_age)
    )

    # Clear minion repo-ng cache see #35342 discussion
    log.info('Removing all *.sls files under \'%s\'', repo_details.local_dest)
    failed = []
    for root, _, files in os.walk(repo_details.local_dest, followlinks=False):
        for name in files:
            if name.endswith('.sls'):
                full_filename = os.path.join(root, name)
                try:
                    os.remove(full_filename)
                except OSError as exc:
                    if exc.errno != errno.ENOENT:
                        log.error('Failed to remove %s: %s', full_filename, exc)
                        failed.append(full_filename)
    if failed:
        raise CommandExecutionError(
            'Failed to clear one or more winrepo cache files',
            info={'failed': failed}
        )

    # Cache repo-ng locally
    __salt__['cp.cache_dir'](
        repo_details.winrepo_source_dir,
        saltenv,
        include_pat='*.sls'
    )

    return genrepo(saltenv=saltenv, verbose=verbose, failhard=failhard)