def get_repo_data(saltenv='base'):
    '''
    Returns the existing package meteadata db. Will create it, if it does not
    exist, however will not refresh it.

    Args:
        saltenv (str): Salt environment. Default ``base``

    Returns:
        dict: A dict containing contents of metadata db.

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.get_repo_data
    '''
    # we only call refresh_db if it does not exist, as we want to return
    # the existing data even if its old, other parts of the code call this,
    # but they will call refresh if they need too.
    repo_details = _get_repo_details(saltenv)

    if repo_details.winrepo_age == -1:
        # no repo meta db
        log.debug('No winrepo.p cache file. Refresh pkg db now.')
        refresh_db(saltenv=saltenv)

    if 'winrepo.data' in __context__:
        log.trace('get_repo_data returning results from __context__')
        return __context__['winrepo.data']
    else:
        log.trace('get_repo_data called reading from disk')

    try:
        serial = salt.payload.Serial(__opts__)
        with salt.utils.files.fopen(repo_details.winrepo_file, 'rb') as repofile:
            try:
                repodata = salt.utils.data.decode(serial.loads(repofile.read(), encoding='utf-8') or {})
                __context__['winrepo.data'] = repodata
                return repodata
            except Exception as exc:
                log.exception(exc)
                return {}
    except IOError as exc:
        log.error('Not able to read repo file')
        log.exception(exc)
        return {}