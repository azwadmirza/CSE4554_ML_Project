def genrepo(**kwargs):
    '''
    Generate package metedata db based on files within the winrepo_source_dir

    Kwargs:

        saltenv (str): Salt environment. Default: ``base``

        verbose (bool):
            Return verbose data structure which includes 'success_list', a list
            of all sls files and the package names contained within.
            Default ``False``.

        failhard (bool):
            If ``True``, an error will be raised if any repo SLS files failed
            to process. If ``False``, no error will be raised, and a dictionary
            containing the full results will be returned.

    .. note::
        - Hidden directories (directories beginning with '`.`', such as
          '`.git`') will be ignored.

    Returns:
        dict: A dictionary of the results of the command

    CLI Example:

    .. code-block:: bash

        salt-run pkg.genrepo
        salt -G 'os:windows' pkg.genrepo verbose=true failhard=false
        salt -G 'os:windows' pkg.genrepo saltenv=base
    '''
    saltenv = kwargs.pop('saltenv', 'base')
    verbose = salt.utils.is_true(kwargs.pop('verbose', False))
    failhard = salt.utils.is_true(kwargs.pop('failhard', True))

    ret = {}
    successful_verbose = {}
    total_files_processed = 0
    ret['repo'] = {}
    ret['errors'] = {}
    repo_details = _get_repo_details(saltenv)

    for root, _, files in os.walk(repo_details.local_dest, followlinks=False):

        # Skip hidden directories (.git)
        if re.search(r'[\\/]\..*', root):
            log.debug('Skipping files in directory: {0}'.format(root))
            continue

        short_path = os.path.relpath(root, repo_details.local_dest)
        if short_path == '.':
            short_path = ''

        for name in files:
            if name.endswith('.sls'):
                total_files_processed += 1
                _repo_process_pkg_sls(
                    os.path.join(root, name),
                    os.path.join(short_path, name),
                    ret,
                    successful_verbose
                    )
    serial = salt.payload.Serial(__opts__)
    # TODO: 2016.11 has PY2 mode as 'w+b' develop has 'w+' ? PY3 is 'wb+'
    # also the reading of this is 'rb' in get_repo_data()
    mode = 'w+' if six.PY2 else 'wb+'

    with salt.utils.fopen(repo_details.winrepo_file, mode) as repo_cache:
        repo_cache.write(serial.dumps(ret))
    # For some reason we can not save ret into __context__['winrepo.data'] as this breaks due to utf8 issues
    successful_count = len(successful_verbose)
    error_count = len(ret['errors'])
    if verbose:
        results = {
            'total': total_files_processed,
            'success': successful_count,
            'failed': error_count,
            'success_list': successful_verbose,
            'failed_list': ret['errors']
            }
    else:
        if error_count > 0:
            results = {
                'total': total_files_processed,
                'success': successful_count,
                'failed': error_count,
                'failed_list': ret['errors']
                }
        else:
            results = {
                'total': total_files_processed,
                'success': successful_count,
                'failed': error_count
                }

    if error_count > 0 and failhard:
        raise CommandExecutionError(
            'Error occurred while generating repo db',
            info=results
        )
    else:
        return results