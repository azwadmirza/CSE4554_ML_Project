def serialize(name,
              dataset=None,
              dataset_pillar=None,
              user=None,
              group=None,
              mode=None,
              env=None,
              backup='',
              makedirs=False,
              show_diff=True,
              create=True,
              merge_if_exists=False,
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
        Write the data as this format. Supported output formats:

        * JSON
        * YAML
        * Python (via pprint.pformat)

    user
        The user to own the directory, this defaults to the user salt is
        running as on the minion

    group
        The group ownership set for the directory, this defaults to the group
        salt is running as on the minion

    mode
        The permissions to set on this file, aka 644, 0775, 4664

    backup
        Overrides the default backup mode for this specific file.

    makedirs
        Create parent directories for destination file.

        .. versionadded:: 2014.1.3

    show_diff
        If set to False, the diff will not be shown.

    create
        Default is True, if create is set to False then the file will only be
        managed if the file already exists on the system.

    merge_if_exists
        Default is False, if merge_if_exists is True then the existing file will
        be parsed and the dataset passed in will be merged with the existing
        content

        .. versionadded:: 2014.7.0

    For example, this state:

    .. code-block:: yaml

        /etc/dummy/package.json:
          file.serialize:
            - dataset:
                name: naive
                description: A package using naive versioning
                author: A confused individual <iam@confused.com>
                dependencies:
                    express: >= 1.2.0
                    optimist: >= 0.1.0
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
    name = os.path.expanduser(name)

    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': True}
    if not name:
        return _error(ret, 'Must provide name to file.serialize')

    if isinstance(env, six.string_types):
        msg = (
            'Passing a salt environment should be done using \'saltenv\' not '
            '\'env\'. This warning will go away in Salt Carbon and this '
            'will be the default and expected behavior. Please update your '
            'state files.'
        )
        salt.utils.warn_until('Carbon', msg)
        ret.setdefault('warnings', []).append(msg)
        # No need to set __env__ = env since that's done in the state machinery

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

    if salt.utils.is_windows():
        if group is not None:
            log.warning(
                'The group argument for {0} has been ignored as this '
                'is a Windows system.'.format(name)
            )
        group = user

    serializer_name = '{0}.serialize'.format(formatter)
    deserializer_name = '{0}.deserialize'.format(formatter)
    if serializer_name in __serializers__:
        serializer = __serializers__[serializer_name]
        if merge_if_exists:
            if os.path.isfile(name):
                if '{0}.deserialize'.format(formatter) in __serializers__:
                    with salt.utils.fopen(name, 'r') as fhr:
                        existing_data = __serializers__[deserializer_name](fhr)
                else:
                    return {'changes': {},
                            'comment': ('{0} format is not supported for merging'
                                        .format(formatter.capitalize())),
                            'name': name,
                            'result': False}

                if existing_data is not None:
                    for k, v in six.iteritems(dataset):
                        if k in existing_data:
                            ret['changes'].update(_merge_dict(existing_data, k, v))
                        else:
                            ret['changes'][k] = v
                            existing_data[k] = v
                    dataset = existing_data

        contents = __serializers__[serializer_name](dataset)
    else:
        return {'changes': {},
                'comment': '{0} format is not supported'.format(
                    formatter.capitalize()),
                'name': name,
                'result': False
                }

    contents += '\n'

    if __opts__['test']:
        ret['changes'] = __salt__['file.check_managed_changes'](
            name=name,
            source=None,
            source_hash={},
            user=user,
            group=group,
            mode=mode,
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
                                        saltenv=__env__,
                                        backup=backup,
                                        makedirs=makedirs,
                                        template=None,
                                        show_diff=show_diff,
                                        contents=contents)