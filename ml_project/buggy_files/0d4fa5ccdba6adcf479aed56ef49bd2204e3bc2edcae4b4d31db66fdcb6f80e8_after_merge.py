def source_list(source, source_hash, saltenv):
    '''
    Check the source list and return the source to use

    CLI Example:

    .. code-block:: bash

        salt '*' file.source_list salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' base
    '''
    contextkey = '{0}_|-{1}_|-{2}'.format(source, source_hash, saltenv)
    if contextkey in __context__:
        return __context__[contextkey]

    # get the master file list
    if isinstance(source, list):
        mfiles = [(f, saltenv) for f in __salt__['cp.list_master'](saltenv)]
        mdirs = [(d, saltenv) for d in __salt__['cp.list_master_dirs'](saltenv)]
        for single in source:
            if isinstance(single, dict):
                single = next(iter(single))

            path, senv = salt.utils.url.parse(single)
            if senv:
                mfiles += [(f, senv) for f in __salt__['cp.list_master'](senv)]
                mdirs += [(d, senv) for d in __salt__['cp.list_master_dirs'](senv)]

        ret = None
        for single in source:
            if isinstance(single, dict):
                # check the proto, if it is http or ftp then download the file
                # to check, if it is salt then check the master list
                # if it is a local file, check if the file exists
                if len(single) != 1:
                    continue
                single_src = next(iter(single))
                single_hash = single[single_src] if single[single_src] else source_hash
                urlparsed_single_src = _urlparse(single_src)
                proto = urlparsed_single_src.scheme
                if proto == 'salt':
                    path, senv = salt.utils.url.parse(single_src)
                    if not senv:
                        senv = saltenv
                    if (path, saltenv) in mfiles or (path, saltenv) in mdirs:
                        ret = (single_src, single_hash)
                        break
                elif proto.startswith('http') or proto == 'ftp':
                    try:
                        if __salt__['cp.cache_file'](single_src):
                            ret = (single_src, single_hash)
                            break
                    except MinionError as exc:
                        # Error downloading file. Log the caught exception and
                        # continue on to the next source.
                        log.exception(exc)
                elif proto == 'file' and os.path.exists(urlparsed_single_src.path):
                    ret = (single_src, single_hash)
                    break
                elif single_src.startswith('/') and os.path.exists(single_src):
                    ret = (single_src, single_hash)
                    break
            elif isinstance(single, six.string_types):
                path, senv = salt.utils.url.parse(single)
                if not senv:
                    senv = saltenv
                if (path, senv) in mfiles or (path, senv) in mdirs:
                    ret = (single, source_hash)
                    break
                urlparsed_src = _urlparse(single)
                proto = urlparsed_src.scheme
                if proto == 'file' and os.path.exists(urlparsed_src.path):
                    ret = (single, source_hash)
                    break
                elif proto.startswith('http') or proto == 'ftp':
                    if __salt__['cp.cache_file'](single):
                        ret = (single, source_hash)
                        break
                elif single.startswith('/') and os.path.exists(single):
                    ret = (single, source_hash)
                    break
        if ret is None:
            # None of the list items matched
            raise CommandExecutionError(
                'none of the specified sources were found'
            )
    else:
        ret = (source, source_hash)

    __context__[contextkey] = ret
    return ret