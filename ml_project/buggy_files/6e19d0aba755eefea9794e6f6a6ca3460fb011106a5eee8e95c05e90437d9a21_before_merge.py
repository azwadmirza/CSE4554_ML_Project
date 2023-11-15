def managed(name,
            source=None,
            source_hash='',
            user=None,
            group=None,
            mode=None,
            template=None,
            makedirs=False,
            context=None,
            replace=True,
            defaults=None,
            env=None,
            backup='',
            show_diff=True,
            create=True,
            contents=None,
            contents_pillar=None,
            **kwargs):
    '''
    Manage a given file, this function allows for a file to be downloaded from
    the salt master and potentially run through a templating system.

    name
        The location of the file to manage

    source
        The source file to download to the minion, this source file can be
        hosted on either the salt master server, or on an HTTP or FTP server.
        For files hosted on the salt file server, if the file is located on
        the master in the directory named spam, and is called eggs, the source
        string is salt://spam/eggs. If source is left blank or None, the file
        will be created as an empty file and the content will not be managed

        If the file is hosted on a HTTP or FTP server then the source_hash
        argument is also required

    source_hash:
        This can be either a file which contains a source hash string for
        the source, or a source hash string. The source hash string is the
        hash algorithm followed by the hash of the file:
        md5=e138491e9d5b97023cea823fe17bac22

        The file can contain checksums for several files, in this case every
        line must consist of full name of the file and checksum separated by
        space:

        Example::

            /etc/rc.conf md5=ef6e82e4006dee563d98ada2a2a80a27
            /etc/resolv.conf sha256=c8525aee419eb649f0233be91c151178b30f0dff8ebbdcc8de71b1d5c8bcc06a


    user
        The user to own the file, this defaults to the user salt is running as
        on the minion

    group
        The group ownership set for the file, this defaults to the group salt
        is running as on the minion

    mode
        The permissions to set on this file, aka 644, 0775, 4664

    template
        If this setting is applied then the named templating engine will be
        used to render the downloaded file, currently jinja, mako, and wempy
        are supported

    makedirs
        If the file is located in a path without a parent directory, then
        the state will fail. If makedirs is set to True, then the parent
        directories will be created to facilitate the creation of the named
        file.

    replace
        If this file should be replaced.  If false, this command will
        not overwrite file contents but will enforce permissions if the file
        exists already.  Default is True.

    context
        Overrides default context variables passed to the template.

    defaults
        Default context passed to the template.

    backup
        Overrides the default backup mode for this specific file.

    show_diff
        If set to False, the diff will not be shown.

    create
        Default is True, if create is set to False then the file will only be
        managed if the file already exists on the system.

    contents
        Default is None.  If specified, will use the given string as the
        contents of the file.  Should not be used in conjunction with a source
        file of any kind.  Ignores hashes and does not use a templating engine.

    contents_pillar
        .. versionadded:: 0.17

        Operates like ``contents``, but draws from a value stored in pillar,
        using the pillar path syntax used in :mod:`pillar.get
        <salt.modules.pillar.get>`. This is useful when the pillar value
        contains newlines, as referencing a pillar variable using a jinja/mako
        template can result in YAML formatting issues due to the newlines
        causing indentation mismatches.
    '''
    # Make sure that leading zeros stripped by YAML loader are added back
    mode = __salt__['config.manage_mode'](mode)

    user = _test_owner(kwargs, user=user)
    ret = {'changes': {},
           'comment': '',
           'name': name,
           'result': True}
    if not create:
        if not os.path.isfile(name):
            # Don't create a file that is not already present
            ret['comment'] = ('File {0} is not present and is not set for '
                              'creation').format(name)
            return ret
    u_check = _check_user(user, group)
    if u_check:
        # The specified user or group do not exist
        return _error(ret, u_check)
    if not os.path.isabs(name):
        return _error(
            ret, 'Specified file {0} is not an absolute path'.format(name))
    if env is None:
        env = kwargs.get('__env__', 'base')

    if os.path.isdir(name):
        ret['comment'] = 'Specified target {0} is a directory'.format(name)
        ret['result'] = False
        return ret

    if context is None:
        context = {}
    elif not isinstance(context, dict):
        return _error(
            ret, 'Context must be formed as a dict')

    if contents and contents_pillar:
        return _error(
            ret, 'Only one of contents and contents_pillar is permitted')

    # If contents_pillar was used, get the pillar data
    if contents_pillar:
        contents = __salt__['pillar.get'](contents_pillar)
        # Make sure file ends in newline
        if not contents.endswith('\n'):
            contents += '\n'

    if not replace and os.path.exists(name):
       # Check and set the permissions if necessary
        ret, perms = __salt__['file.check_perms'](name,
                                                  ret,
                                                  user,
                                                  group,
                                                  mode)
        if __opts__['test']:
            ret['comment'] = 'File {0} not updated'.format(name)
        elif not ret['changes'] and ret['result']:
            ret['comment'] = ('File {0} exists with proper permissions. '
                              'No changes made.'.format(name))
        return ret

    if name in _ACCUMULATORS:
        if not context:
            context = {}
        context['accumulator'] = _ACCUMULATORS[name]

    if __opts__['test']:
        ret['result'], ret['comment'] = __salt__['file.check_managed'](
            name,
            source,
            source_hash,
            user,
            group,
            mode,
            template,
            makedirs,
            context,
            defaults,
            env,
            contents,
            **kwargs
        )
        return ret

    # If the source is a list then find which file exists
    source, source_hash = __salt__['file.source_list'](
        source,
        source_hash,
        env
    )

    # Gather the source file from the server
    sfn, source_sum, comment_ = __salt__['file.get_managed'](
        name,
        template,
        source,
        source_hash,
        user,
        group,
        mode,
        env,
        context,
        defaults,
        **kwargs
    )
    if comment_ and contents is None:
        return _error(ret, comment_)
    else:
        return __salt__['file.manage_file'](name,
                                            sfn,
                                            ret,
                                            source,
                                            source_sum,
                                            user,
                                            group,
                                            mode,
                                            env,
                                            backup,
                                            template,
                                            show_diff,
                                            contents)