def serialize(name,
              dataset=None,
              dataset_pillar=None,
              user=None,
              group=None,
              mode=None,
              backup='',
              makedirs=False,
              show_changes=True,
              create=True,
              merge_if_exists=False,
              encoding=None,
              encoding_errors='strict',
              serializer_opts=None,
              **kwargs):
    '''
    Serializes dataset and store it into managed file. Useful for sharing
    simple configuration files.

    name
        The location of the file to create

    dataset
        The dataset that will be serialized

    dataset_pillar
        Operates like ``dataset``, but draws from a value stored in pillar,
        using the pillar path syntax used in :mod:`pillar.get
        <salt.modules.pillar.get>`. This is useful when the pillar value
        contains newlines, as referencing a pillar variable using a jinja/mako
        template can result in YAML formatting issues due to the newlines
        causing indentation mismatches.

        .. versionadded:: 2015.8.0

    formatter
        Write the data as this format. See the list of :py:mod:`serializer
        modules <salt.serializers>` for supported output formats.

    encoding
        If specified, then the specified encoding will be used. Otherwise, the
        file will be encoded using the system locale (usually UTF-8). See
        https://docs.python.org/3/library/codecs.html#standard-encodings for
        the list of available encodings.

        .. versionadded:: 2017.7.0

    encoding_errors : 'strict'
        Error encoding scheme. Default is ```'strict'```.
        See https://docs.python.org/2/library/codecs.html#codec-base-classes
        for the list of available schemes.

        .. versionadded:: 2017.7.0

    user
        The user to own the directory, this defaults to the user salt is
        running as on the minion

    group
        The group ownership set for the directory, this defaults to the group
        salt is running as on the minion

    mode
        The permissions to set on this file, e.g. ``644``, ``0775``, or
        ``4664``.

        The default mode for new files and directories corresponds umask of salt
        process. For existing files and directories it's not enforced.

        .. note::
            This option is **not** supported on Windows.

    backup
        Overrides the default backup mode for this specific file.

    makedirs
        Create parent directories for destination file.

        .. versionadded:: 2014.1.3

    show_changes
        Output a unified diff of the old file and the new file. If ``False``
        return a boolean if any changes were made.

    create
        Default is True, if create is set to False then the file will only be
        managed if the file already exists on the system.

    merge_if_exists
        Default is False, if merge_if_exists is True then the existing file will
        be parsed and the dataset passed in will be merged with the existing
        content

        .. versionadded:: 2014.7.0

    serializer_opts
        Pass through options to serializer. For example:

        .. code-block:: yaml

           /etc/dummy/package.yaml
             file.serialize:
               - formatter: yaml
               - serializer_opts:
                 - explicit_start: True
                 - default_flow_style: True
                 - indent: 4

        The valid opts are the additional opts (i.e. not the data being
        serialized) for the function used to serialize the data. Documentation
        for the these functions can be found in the list below:

        - For **yaml**: `yaml.dump()`_
        - For **json**: `json.dumps()`_
        - For **python**: `pprint.pformat()`_

        .. _`yaml.dump()`: https://pyyaml.org/wiki/PyYAMLDocumentation
        .. _`json.dumps()`: https://docs.python.org/2/library/json.html#json.dumps
        .. _`pprint.pformat()`: https://docs.python.org/2/library/pprint.html#pprint.pformat

        .. versionadded:: Fluorine

    For example, this state:

    .. code-block:: yaml

        /etc/dummy/package.json:
          file.serialize:
            - dataset:
                name: naive
                description: A package using naive versioning
                author: A confused individual <iam@confused.com>
                dependencies:
                  express: '>= 1.2.0'
                  optimist: '>= 0.1.0'
                engine: node 0.4.1
            - formatter: json

    will manage the file ``/etc/dummy/package.json``:

    .. code-block:: json

        {
          "author": "A confused individual <iam@confused.com>",
          "dependencies": {
            "express": ">= 1.2.0",
            "optimist": ">= 0.1.0"
          },
          "description": "A package using naive versioning",
          "engine": "node 0.4.1",
          "name": "naive"
        }
    '''
    if 'env' in kwargs:
        # "env" is not supported; Use "saltenv".
        kwargs.pop('env')

    name = os.path.expanduser(name)

    # Set some defaults
    options = {
        'yaml.serialize': {
            'default_flow_style': False,
        },
        'json.serialize': {
            'indent': 2,
            'separators': (',', ': '),
            'sort_keys': True,
        }
    }
    if encoding:
        options['yaml.serialize'].update({'allow_unicode': True})
        options['json.serialize'].update({'ensure_ascii': False})

    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': True}
    if not name:
        return _error(ret, 'Must provide name to file.serialize')

    if not create:
        if not os.path.isfile(name):
            # Don't create a file that is not already present
            ret['comment'] = ('File {0} is not present and is not set for '
                              'creation').format(name)
            return ret

    formatter = kwargs.pop('formatter', 'yaml').lower()

    if len([x for x in (dataset, dataset_pillar) if x]) > 1:
        return _error(
            ret, 'Only one of \'dataset\' and \'dataset_pillar\' is permitted')

    if dataset_pillar:
        dataset = __salt__['pillar.get'](dataset_pillar)

    if dataset is None:
        return _error(
            ret, 'Neither \'dataset\' nor \'dataset_pillar\' was defined')

    if salt.utils.platform.is_windows():
        if group is not None:
            log.warning(
                'The group argument for %s has been ignored as this '
                'is a Windows system.', name
            )
        group = user

    serializer_name = '{0}.serialize'.format(formatter)
    deserializer_name = '{0}.deserialize'.format(formatter)

    if serializer_name not in __serializers__:
        return {'changes': {},
                'comment': '{0} format is not supported'.format(
                    formatter.capitalize()),
                'name': name,
                'result': False
                }

    if serializer_opts:
        if not options.get(serializer_name, {}):
            options[serializer_name] = {}

        options.get(serializer_name, {}).update(
            salt.utils.data.repack_dictlist(serializer_opts)
        )

    if merge_if_exists:
        if os.path.isfile(name):
            if '{0}.deserialize'.format(formatter) not in __serializers__:
                return {'changes': {},
                        'comment': ('{0} format is not supported for merging'
                                    .format(formatter.capitalize())),
                        'name': name,
                        'result': False}

            with salt.utils.files.fopen(name, 'r') as fhr:
                try:
                    existing_data = __serializers__[deserializer_name](fhr, **options.get(serializer_name, {}))
                except (TypeError, salt.serializers.DeserializationError):
                    log.debug('DeserializationError exception caught, trying to merge without serializer_opts: %s', options.get(serializer_name, {}))
                    fhr.seek(0)
                    existing_data = __serializers__[deserializer_name](fhr)

            if existing_data is not None:
                merged_data = salt.utils.dictupdate.merge_recurse(existing_data, dataset)
                if existing_data == merged_data:
                    ret['result'] = True
                    ret['comment'] = 'The file {0} is in the correct state'.format(name)
                    return ret
                dataset = merged_data
    contents = __serializers__[serializer_name](dataset, **options.get(serializer_name, {}))

    contents += '\n'

    # Make sure that any leading zeros stripped by YAML loader are added back
    mode = salt.utils.files.normalize_mode(mode)

    if __opts__['test']:
        ret['changes'] = __salt__['file.check_managed_changes'](
            name=name,
            source=None,
            source_hash={},
            source_hash_name=None,
            user=user,
            group=group,
            mode=mode,
            attrs=None,
            template=None,
            context=None,
            defaults=None,
            saltenv=__env__,
            contents=contents,
            skip_verify=False,
            **kwargs
        )

        if ret['changes']:
            ret['result'] = None
            ret['comment'] = 'Dataset will be serialized and stored into {0}'.format(
                name)

            if not show_changes:
                ret['changes']['diff'] = '<show_changes=False>'
        else:
            ret['result'] = True
            ret['comment'] = 'The file {0} is in the correct state'.format(name)
        return ret

    return __salt__['file.manage_file'](name=name,
                                        sfn='',
                                        ret=ret,
                                        source=None,
                                        source_sum={},
                                        user=user,
                                        group=group,
                                        mode=mode,
                                        attrs=None,
                                        saltenv=__env__,
                                        backup=backup,
                                        makedirs=makedirs,
                                        template=None,
                                        show_changes=show_changes,
                                        encoding=encoding,
                                        encoding_errors=encoding_errors,
                                        contents=contents)