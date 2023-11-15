def get_managed(
        name,
        template,
        source,
        source_hash,
        source_hash_name,
        user,
        group,
        mode,
        saltenv,
        context,
        defaults,
        skip_verify=False,
        **kwargs):
    '''
    Return the managed file data for file.managed

    name
        location where the file lives on the server

    template
        template format

    source
        managed source file

    source_hash
        hash of the source file

    source_hash_name
        When ``source_hash`` refers to a remote file, this specifies the
        filename to look for in that file.

        .. versionadded:: 2016.3.5

    user
        Owner of file

    group
        Group owner of file

    mode
        Permissions of file

    context
        Variables to add to the template context

    defaults
        Default values of for context_dict

    skip_verify
        If ``True``, hash verification of remote file sources (``http://``,
        ``https://``, ``ftp://``) will be skipped, and the ``source_hash``
        argument will be ignored.

        .. versionadded:: 2016.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_managed /etc/httpd/conf.d/httpd.conf jinja salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' None root root '755' base None None
    '''
    # Copy the file to the minion and templatize it
    sfn = ''
    source_sum = {}

    def _get_local_file_source_sum(path):
        '''
        DRY helper for getting the source_sum value from a locally cached
        path.
        '''
        return {'hsum': get_hash(path, form='sha256'), 'hash_type': 'sha256'}

    # If we have a source defined, let's figure out what the hash is
    if source:
        urlparsed_source = _urlparse(source)
        parsed_scheme = urlparsed_source.scheme
        parsed_path = os.path.join(
                urlparsed_source.netloc, urlparsed_source.path).rstrip(os.sep)

        if parsed_scheme and parsed_scheme.lower() in 'abcdefghijklmnopqrstuvwxyz':
            parsed_path = ':'.join([parsed_scheme, parsed_path])
            parsed_scheme = 'file'

        if parsed_scheme == 'salt':
            source_sum = __salt__['cp.hash_file'](source, saltenv)
            if not source_sum:
                return '', {}, 'Source file {0} not found'.format(source)
        elif not source_hash and parsed_scheme == 'file':
            source_sum = _get_local_file_source_sum(parsed_path)
        elif not source_hash and source.startswith(os.sep):
            source_sum = _get_local_file_source_sum(source)
        else:
            if not skip_verify:
                if source_hash:
                    try:
                        source_sum = get_source_sum(name,
                                                    source,
                                                    source_hash,
                                                    source_hash_name,
                                                    saltenv)
                    except CommandExecutionError as exc:
                        return '', {}, exc.strerror
                else:
                    msg = (
                        'Unable to verify upstream hash of source file {0}, '
                        'please set source_hash or set skip_verify to True'
                        .format(source)
                    )
                    return '', {}, msg

    if source and (template or parsed_scheme in salt.utils.files.REMOTE_PROTOS):
        # Check if we have the template or remote file cached
        cache_refetch = False
        cached_dest = __salt__['cp.is_cached'](source, saltenv)
        if cached_dest and (source_hash or skip_verify):
            htype = source_sum.get('hash_type', 'sha256')
            cached_sum = get_hash(cached_dest, form=htype)
            if skip_verify:
                # prev: if skip_verify or cached_sum == source_sum['hsum']:
                # but `cached_sum == source_sum['hsum']` is elliptical as prev if
                sfn = cached_dest
                source_sum = {'hsum': cached_sum, 'hash_type': htype}
            elif cached_sum != source_sum.get('hsum', __opts__['hash_type']):
                cache_refetch = True

        # If we didn't have the template or remote file, let's get it
        # Similarly when the file has been updated and the cache has to be refreshed
        if not sfn or cache_refetch:
            try:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            except Exception as exc:
                # A 404 or other error code may raise an exception, catch it
                # and return a comment that will fail the calling state.
                return '', {}, 'Failed to cache {0}: {1}'.format(source, exc)

        # If cache failed, sfn will be False, so do a truth check on sfn first
        # as invoking os.path.exists() on a bool raises a TypeError.
        if not sfn or not os.path.exists(sfn):
            return sfn, {}, 'Source file \'{0}\' not found'.format(source)
        if sfn == name:
            raise SaltInvocationError(
                'Source file cannot be the same as destination'
            )

        if template:
            if template in salt.utils.templates.TEMPLATE_REGISTRY:
                context_dict = defaults if defaults else {}
                if context:
                    context_dict.update(context)
                data = salt.utils.templates.TEMPLATE_REGISTRY[template](
                    sfn,
                    name=name,
                    source=source,
                    user=user,
                    group=group,
                    mode=mode,
                    saltenv=saltenv,
                    context=context_dict,
                    salt=__salt__,
                    pillar=__pillar__,
                    grains=__opts__['grains'],
                    opts=__opts__,
                    **kwargs)
            else:
                return sfn, {}, ('Specified template format {0} is not supported'
                                 ).format(template)

            if data['result']:
                sfn = data['data']
                hsum = get_hash(sfn, form='sha256')
                source_sum = {'hash_type': 'sha256',
                              'hsum': hsum}
            else:
                __clean_tmp(sfn)
                return sfn, {}, data['data']

    return sfn, source_sum, ''