def serialize(name,
              dataset,
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
        the dataset that will be serialized

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

    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': True}

    if isinstance(env, salt._compat.string_types):
        msg = (
            'Passing a salt environment should be done using \'saltenv\' not '
            '\'env\'. This warning will go away in Salt Boron and this '
            'will be the default and expected behavior. Please update your '
            'state files.'
        )
        salt.utils.warn_until('Boron', msg)
        ret.setdefault('warnings', []).append(msg)
        # No need to set __env__ = env since that's done in the state machinery

    if not create:
        if not os.path.isfile(name):
            # Don't create a file that is not already present
            ret['comment'] = ('File {0} is not present and is not set for '
                              'creation').format(name)
            return ret

    formatter = kwargs.pop('formatter', 'yaml').lower()

    if merge_if_exists:
        if os.path.isfile(name):
            if formatter == 'yaml':
                existing_data = yaml.safe_load(file(name, 'r'))
            elif formatter == 'json':
                existing_data = json.load(file(name, 'r'))
            else:
                return {'changes': {},
                        'comment': ('{0} format is not supported for merging'
                                    .format(formatter.capitalized())),
                        'name': name,
                        'result': False}

            if existing_data is not None:
                for k, v in dataset.iteritems():
                    if k in existing_data:
                        ret['changes'].update(_merge_dict(existing_data, k, v))
                    else:
                        ret['changes'][k] = v
                        existing_data[k] = v
                dataset = existing_data

    if formatter == 'yaml':
        contents = yaml_serializer.serialize(dataset,
                                             default_flow_style=False)
    elif formatter == 'json':
        contents = json_serializer.serialize(dataset,
                                             indent=2,
                                             separators=(',', ': '),
                                             sort_keys=True)
    elif formatter == 'python':
        # round-trip this through JSON to avoid OrderedDict types
        # there's probably a more performant way to do this...
        # TODO remove json round-trip when all dataset will use
        # utils.serializers
        contents = pprint.pformat(
            json.loads(
                json.dumps(dataset),
                object_hook=salt.utils.decode_dict
            )
        )
    else:
        return {'changes': {},
                'comment': '{0} format is not supported'.format(
                    formatter.capitalized()),
                'name': name,
                'result': False
                }

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