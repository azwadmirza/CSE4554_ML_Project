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

    default
        default values of for context_dict


    CLI Example:

    .. code-block:: bash

        salt '*' file.get_managed /etc/httpd/conf.d/httpd.conf jinja salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' root root '755' base None None
    '''
    # Copy the file to the minion and templatize it
    sfn = ''
    source_sum = {}
    # if we have a source defined, lets figure out what the hash is
    if source:
        urlparsed_source = _urlparse(source)
        if urlparsed_source.scheme == 'salt':
            source_sum = __salt__['cp.hash_file'](source, saltenv)
            if not source_sum:
                return '', {}, 'Source file {0} not found'.format(source)
        elif source_hash:
            protos = ('salt', 'http', 'https', 'ftp', 'swift', 's3')
            if _urlparse(source_hash).scheme in protos:
                # The source_hash is a file on a server
                hash_fn = __salt__['cp.cache_file'](source_hash, saltenv)
                if not hash_fn:
                    return '', {}, 'Source hash file {0} not found'.format(
                        source_hash)
                source_sum = extract_hash(hash_fn, '', name)
                if source_sum is None:
                    return '', {}, ('Source hash file {0} contains an invalid '
                        'hash format, it must be in the format <hash type>=<hash>.'
                        ).format(source_hash)

            else:
                # The source_hash is a hash string
                comps = source_hash.split('=')
                if len(comps) < 2:
                    return '', {}, ('Source hash file {0} contains an '
                                    'invalid hash format, it must be in '
                                    'the format <hash type>=<hash>'
                                    ).format(source_hash)
                source_sum['hsum'] = comps[1].strip()
                source_sum['hash_type'] = comps[0].strip()
        elif urlparsed_source.scheme == 'file':
            file_sum = get_hash(urlparsed_source.path, form='sha256')
            source_sum = {'hsum': file_sum, 'hash_type': 'sha256'}
        elif source.startswith('/'):
            file_sum = get_hash(source, form='sha256')
            source_sum = {'hsum': file_sum, 'hash_type': 'sha256'}
        else:
            return '', {}, ('Unable to determine upstream hash of'
                            ' source file {0}').format(source)

    # if the file is a template we need to actually template the file to get
    # a checksum, but we can cache the template itself, but only if there is
    # a template source (it could be a templated contents)
    if template and source:
        # check if we have the template cached
        template_dest = __salt__['cp.is_cached'](source, saltenv)
        if template_dest and source_hash:
            comps = source_hash.split('=')
            cached_template_sum = get_hash(template_dest, form=source_sum['hash_type'])
            if cached_template_sum == source_sum['hsum']:
                sfn = template_dest
        # if we didn't have the template file, lets get it
        if not sfn:
            sfn = __salt__['cp.cache_file'](source, saltenv)

        # exists doesn't play nice with sfn as bool
        # but if cache failed, sfn == False
        if not sfn or not os.path.exists(sfn):
            return sfn, {}, 'Source file {0!r} not found'.format(source)
        if sfn == name:
            raise SaltInvocationError(
                'Source file cannot be the same as destination'
            )
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
            hsum = get_hash(sfn)
            source_sum = {'hash_type': 'sha256',
                          'hsum': hsum}
        else:
            __clean_tmp(sfn)
            return sfn, {}, data['data']

    return sfn, source_sum, ''