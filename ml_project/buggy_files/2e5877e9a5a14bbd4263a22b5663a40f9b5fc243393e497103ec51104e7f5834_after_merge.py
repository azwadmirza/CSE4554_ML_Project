def refresh_db(**kwargs):
    r'''
    Generates the local software metadata database (`winrepo.p`) on the minion.
    The database is stored in a serialized format located by default at the
    following location:

    `C:\salt\var\cache\salt\minion\files\base\win\repo-ng\winrepo.p`

    This module performs the following steps to generate the software metadata
    database:

    - Fetch the package definition files (.sls) from `winrepo_source_dir`
      (default `salt://win/repo-ng`) and cache them in
      `<cachedir>\files\<saltenv>\<winrepo_source_dir>`
      (default: `C:\salt\var\cache\salt\minion\files\base\win\repo-ng`)
    - Call :py:func:`pkg.genrepo <salt.modules.win_pkg.genrepo>` to parse the
      package definition files and generate the repository metadata database
      file (`winrepo.p`)
    - Return the report received from
      :py:func:`pkg.genrepo <salt.modules.win_pkg.genrepo>`

    The default winrepo directory on the master is `/srv/salt/win/repo-ng`. All
    files that end with `.sls` in this and all subdirectories will be used to
    generate the repository metadata database (`winrepo.p`).

    .. note::
        - Hidden directories (directories beginning with '`.`', such as
          '`.git`') will be ignored.

    .. note::
        There is no need to call `pkg.refresh_db` every time you work with the
        pkg module. Automatic refresh will occur based on the following minion
        configuration settings:
            - `winrepo_cache_expire_min`
            - `winrepo_cache_expire_max`
        However, if the package definition files have changed, as would be the
        case if you are developing a new package definition, this function
        should be called to ensure the minion has the latest information about
        packages available to it.

    .. warning::
        Directories and files fetched from <winrepo_source_dir>
        (`/srv/salt/win/repo-ng`) will be processed in alphabetical order. If
        two or more software definition files contain the same name, the last
        one processed replaces all data from the files processed before it.

    For more information see
    :ref:`Windows Software Repository <windows-package-manager>`

    Kwargs:

        saltenv (str): Salt environment. Default: ``base``

        verbose (bool):
            Return a verbose data structure which includes 'success_list', a
            list of all sls files and the package names contained within.
            Default is 'False'

        failhard (bool):
            If ``True``, an error will be raised if any repo SLS files fails to
            process. If ``False``, no error will be raised, and a dictionary
            containing the full results will be returned.

    Returns:
        dict: A dictionary containing the results of the database refresh.

    .. note::
        A result with a `total: 0` generally means that the files are in the
        wrong location on the master. Try running the following command on the
        minion: `salt-call -l debug pkg.refresh saltenv=base`

    .. warning::
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
    log.info('Fetching *.sls files from {0}'.format(repo_details.winrepo_source_dir))
    __salt__['cp.cache_dir'](
        path=repo_details.winrepo_source_dir,
        saltenv=saltenv,
        include_pat='*.sls',
        exclude_pat=r'E@\/\..*?\/'  # Exclude all hidden directories (.git)
    )

    return genrepo(saltenv=saltenv, verbose=verbose, failhard=failhard)