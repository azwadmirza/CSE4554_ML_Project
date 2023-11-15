def get_managed(
        name,
        template,
        source,
        source_hash,
        user,
        group,
        mode,
        saltenv,
        context,
        defaults,
        skip_verify,
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

    user
        user owner

    group
        group owner

    mode
        file mode

    context
        variables to add to the environment

    defaults
        default values of for context_dict

    skip_verify
        If ``True``, hash verification of remote file sources (``http://``,
        ``https://``, ``ftp://``) will be skipped, and the ``source_hash``
        argument will be ignored.

        .. versionadded:: 2016.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_managed /etc/httpd/conf.d/httpd.conf jinja salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' root root '755' base None None
    '''
    # Copy the file to the minion and templatize it
    sfn = ''
    source_sum = {}
    remote_protos = ('http', 'https', 'ftp', 'swift', 's3')

    def _get_local_file_source_sum(path):
        '''
        DRY helper for getting the source_sum value from a locally cached
        path.
        '''
        return {'hsum': get_hash(path, form='sha256'), 'hash_type': 'sha256'}

    source_hash_name = kwargs.pop('source_hash_name', None)
    # If we have a source defined, let's figure out what the hash is
    if source:
        urlparsed_source = _urlparse(source)
        if urlparsed_source.scheme == 'salt':
            source_sum = __salt__['cp.hash_file'](source, saltenv)
            if not source_sum:
                return '', {}, 'Source file {0} not found'.format(source)
        elif not source_hash and urlparsed_source.scheme == 'file':
            source_sum = _get_local_file_source_sum(urlparsed_source.path)
        elif not source_hash and source.startswith('/'):
            source_sum = _get_local_file_source_sum(source)
        else:
            if not skip_verify:
                if source_hash:
                    protos = ('salt', 'file') + remote_protos

                    def _invalid_source_hash_format():
                        '''
                        DRY helper for reporting invalid source_hash input
                        '''
                        msg = (
                            'Source hash {0} format is invalid. It '
                            'must be in the format <hash type>=<hash>, '
                            'or it must be a supported protocol: {1}'
                            .format(source_hash, ', '.join(protos))
                        )
                        return '', {}, msg

                    try:
                        source_hash_scheme = _urlparse(source_hash).scheme
                    except TypeError:
                        return '', {}, ('Invalid format for source_hash '
                                        'parameter')
                    if source_hash_scheme in protos:
                        # The source_hash is a file on a server
                        hash_fn = __salt__['cp.cache_file'](
                            source_hash, saltenv)
                        if not hash_fn:
                            return '', {}, ('Source hash file {0} not found'
                                            .format(source_hash))
                        source_sum = extract_hash(
                            hash_fn, '', source_hash_name or name)
                        if source_sum is None:
                            return _invalid_source_hash_format()

                    else:
                        # The source_hash is a hash string
                        comps = source_hash.split('=', 1)
                        if len(comps) < 2:
                            return _invalid_source_hash_format()
                        source_sum['hsum'] = comps[1].strip()
                        source_sum['hash_type'] = comps[0].strip()
                else:
                    msg = (
                        'Unable to verify upstream hash of source file {0}, '
                        'please set source_hash or set skip_verify to True'
                        .format(source)
                    )
                    return '', {}, msg

    if source and (template or urlparsed_source.scheme in remote_protos):
        # Check if we have the template or remote file cached
        cached_dest = __salt__['cp.is_cached'](source, saltenv)
        if cached_dest and (source_hash or skip_verify):
            htype = source_sum.get('hash_type', 'sha256')
            cached_sum = get_hash(cached_dest, form=htype)
            if skip_verify or cached_sum == source_sum['hsum']:
                sfn = cached_dest
                source_sum = {'hsum': cached_sum, 'hash_type': htype}

        # If we didn't have the template or remote file, let's get it
        if not sfn:
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
                    grains=__grains__,
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