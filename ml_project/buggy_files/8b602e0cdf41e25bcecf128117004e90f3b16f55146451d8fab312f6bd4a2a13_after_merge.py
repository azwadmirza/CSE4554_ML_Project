def managed(name,
            source=None,
            source_hash='',
            source_hash_name=None,
            keep_source=True,
            user=None,
            group=None,
            mode=None,
            attrs=None,
            template=None,
            makedirs=False,
            dir_mode=None,
            context=None,
            replace=True,
            defaults=None,
            backup='',
            show_changes=True,
            create=True,
            contents=None,
            tmp_ext='',
            contents_pillar=None,
            contents_grains=None,
            contents_newline=True,
            contents_delimiter=':',
            encoding=None,
            encoding_errors='strict',
            allow_empty=True,
            follow_symlinks=True,
            check_cmd=None,
            skip_verify=False,
            win_owner=None,
            win_perms=None,
            win_deny_perms=None,
            win_inheritance=True,
            win_perms_reset=False,
            **kwargs):
    r'''
    Manage a given file, this function allows for a file to be downloaded from
    the salt master and potentially run through a templating system.

    name
        The location of the file to manage, as an absolute path.

    source
        The source file to download to the minion, this source file can be
        hosted on either the salt master server (``salt://``), the salt minion
        local file system (``/``), or on an HTTP or FTP server (``http(s)://``,
        ``ftp://``).

        Both HTTPS and HTTP are supported as well as downloading directly
        from Amazon S3 compatible URLs with both pre-configured and automatic
        IAM credentials. (see s3.get state documentation)
        File retrieval from Openstack Swift object storage is supported via
        swift://container/object_path URLs, see swift.get documentation.
        For files hosted on the salt file server, if the file is located on
        the master in the directory named spam, and is called eggs, the source
        string is salt://spam/eggs. If source is left blank or None
        (use ~ in YAML), the file will be created as an empty file and
        the content will not be managed. This is also the case when a file
        already exists and the source is undefined; the contents of the file
        will not be changed or managed.

        If the file is hosted on a HTTP or FTP server then the source_hash
        argument is also required.

        A list of sources can also be passed in to provide a default source and
        a set of fallbacks. The first source in the list that is found to exist
        will be used and subsequent entries in the list will be ignored. Source
        list functionality only supports local files and remote files hosted on
        the salt master server or retrievable via HTTP, HTTPS, or FTP.

        .. code-block:: yaml

            file_override_example:
              file.managed:
                - source:
                  - salt://file_that_does_not_exist
                  - salt://file_that_exists

    source_hash
        This can be one of the following:
            1. a source hash string
            2. the URI of a file that contains source hash strings

        The function accepts the first encountered long unbroken alphanumeric
        string of correct length as a valid hash, in order from most secure to
        least secure:

        .. code-block:: text

            Type    Length
            ======  ======
            sha512     128
            sha384      96
            sha256      64
            sha224      56
            sha1        40
            md5         32

        **Using a Source Hash File**
            The file can contain several checksums for several files. Each line
            must contain both the file name and the hash.  If no file name is
            matched, the first hash encountered will be used, otherwise the most
            secure hash with the correct source file name will be used.

            When using a source hash file the source_hash argument needs to be a
            url, the standard download urls are supported, ftp, http, salt etc:

            Example:

            .. code-block:: yaml

                tomdroid-src-0.7.3.tar.gz:
                  file.managed:
                    - name: /tmp/tomdroid-src-0.7.3.tar.gz
                    - source: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.tar.gz
                    - source_hash: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.hash

            The following lines are all supported formats:

            .. code-block:: text

                /etc/rc.conf ef6e82e4006dee563d98ada2a2a80a27
                sha254c8525aee419eb649f0233be91c151178b30f0dff8ebbdcc8de71b1d5c8bcc06a  /etc/resolv.conf
                ead48423703509d37c4a90e6a0d53e143b6fc268

            Debian file type ``*.dsc`` files are also supported.

        **Inserting the Source Hash in the SLS Data**

        The source_hash can be specified as a simple checksum, like so:

        .. code-block:: yaml

            tomdroid-src-0.7.3.tar.gz:
              file.managed:
                - name: /tmp/tomdroid-src-0.7.3.tar.gz
                - source: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.tar.gz
                - source_hash: 79eef25f9b0b2c642c62b7f737d4f53f

        .. note::
            Releases prior to 2016.11.0 must also include the hash type, like
            in the below example:

            .. code-block:: yaml

                tomdroid-src-0.7.3.tar.gz:
                  file.managed:
                    - name: /tmp/tomdroid-src-0.7.3.tar.gz
                    - source: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.tar.gz
                    - source_hash: md5=79eef25f9b0b2c642c62b7f737d4f53f

        Known issues:
            If the remote server URL has the hash file as an apparent
            sub-directory of the source file, the module will discover that it
            has already cached a directory where a file should be cached. For
            example:

            .. code-block:: yaml

                tomdroid-src-0.7.3.tar.gz:
                  file.managed:
                    - name: /tmp/tomdroid-src-0.7.3.tar.gz
                    - source: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.tar.gz
                    - source_hash: https://launchpad.net/tomdroid/beta/0.7.3/+download/tomdroid-src-0.7.3.tar.gz/+md5

    source_hash_name
        When ``source_hash`` refers to a hash file, Salt will try to find the
        correct hash by matching the filename/URI associated with that hash. By
        default, Salt will look for the filename being managed. When managing a
        file at path ``/tmp/foo.txt``, then the following line in a hash file
        would match:

        .. code-block:: text

            acbd18db4cc2f85cedef654fccc4a4d8    foo.txt

        However, sometimes a hash file will include multiple similar paths:

        .. code-block:: text

            37b51d194a7513e45b56f6524f2d51f2    ./dir1/foo.txt
            acbd18db4cc2f85cedef654fccc4a4d8    ./dir2/foo.txt
            73feffa4b7f6bb68e44cf984c85f6e88    ./dir3/foo.txt

        In cases like this, Salt may match the incorrect hash. This argument
        can be used to tell Salt which filename to match, to ensure that the
        correct hash is identified. For example:

        .. code-block:: yaml

            /tmp/foo.txt:
              file.managed:
                - source: https://mydomain.tld/dir2/foo.txt
                - source_hash: https://mydomain.tld/hashes
                - source_hash_name: ./dir2/foo.txt

        .. note::
            This argument must contain the full filename entry from the
            checksum file, as this argument is meant to disambiguate matches
            for multiple files that have the same basename. So, in the
            example above, simply using ``foo.txt`` would not match.

        .. versionadded:: 2016.3.5

    keep_source : True
        Set to ``False`` to discard the cached copy of the source file once the
        state completes. This can be useful for larger files to keep them from
        taking up space in minion cache. However, keep in mind that discarding
        the source file will result in the state needing to re-download the
        source file if the state is run again.

        .. versionadded:: 2017.7.3

    user
        The user to own the file, this defaults to the user salt is running as
        on the minion

    group
        The group ownership set for the file, this defaults to the group salt
        is running as on the minion. On Windows, this is ignored

    mode
        The permissions to set on this file, e.g. ``644``, ``0775``, or
        ``4664``.

        The default mode for new files and directories corresponds to the
        umask of the salt process. The mode of existing files and directories
        will only be changed if ``mode`` is specified.

        .. note::
            This option is **not** supported on Windows.

        .. versionchanged:: 2016.11.0
            This option can be set to ``keep``, and Salt will keep the mode
            from the Salt fileserver. This is only supported when the
            ``source`` URL begins with ``salt://``, or for files local to the
            minion. Because the ``source`` option cannot be used with any of
            the ``contents`` options, setting the ``mode`` to ``keep`` is also
            incompatible with the ``contents`` options.

        .. note:: keep does not work with salt-ssh.

            As a consequence of how the files are transferred to the minion, and
            the inability to connect back to the master with salt-ssh, salt is
            unable to stat the file as it exists on the fileserver and thus
            cannot mirror the mode on the salt-ssh minion

    attrs
        The attributes to have on this file, e.g. ``a``, ``i``. The attributes
        can be any or a combination of the following characters:
        ``acdijstuADST``.

        .. note::
            This option is **not** supported on Windows.

        .. versionadded:: 2018.3.0

    template
        If this setting is applied, the named templating engine will be used to
        render the downloaded file. The following templates are supported:

        - :mod:`cheetah<salt.renderers.cheetah>`
        - :mod:`genshi<salt.renderers.genshi>`
        - :mod:`jinja<salt.renderers.jinja>`
        - :mod:`mako<salt.renderers.mako>`
        - :mod:`py<salt.renderers.py>`
        - :mod:`wempy<salt.renderers.wempy>`

    makedirs : False
        If set to ``True``, then the parent directories will be created to
        facilitate the creation of the named file. If ``False``, and the parent
        directory of the destination file doesn't exist, the state will fail.

    dir_mode
        If directories are to be created, passing this option specifies the
        permissions for those directories. If this is not set, directories
        will be assigned permissions by adding the execute bit to the mode of
        the files.

        The default mode for new files and directories corresponds umask of salt
        process. For existing files and directories it's not enforced.

    replace : True
        If set to ``False`` and the file already exists, the file will not be
        modified even if changes would otherwise be made. Permissions and
        ownership will still be enforced, however.

    context
        Overrides default context variables passed to the template.

    defaults
        Default context passed to the template.

    backup
        Overrides the default backup mode for this specific file. See
        :ref:`backup_mode documentation <file-state-backups>` for more details.

    show_changes
        Output a unified diff of the old file and the new file. If ``False``
        return a boolean if any changes were made.

    create : True
        If set to ``False``, then the file will only be managed if the file
        already exists on the system.

    contents
        Specify the contents of the file. Cannot be used in combination with
        ``source``. Ignores hashes and does not use a templating engine.

        This value can be either a single string, a multiline YAML string or a
        list of strings.  If a list of strings, then the strings will be joined
        together with newlines in the resulting file. For example, the below
        two example states would result in identical file contents:

        .. code-block:: yaml

            /path/to/file1:
              file.managed:
                - contents:
                  - This is line 1
                  - This is line 2

            /path/to/file2:
              file.managed:
                - contents: |
                    This is line 1
                    This is line 2


    contents_pillar
        .. versionadded:: 0.17.0
        .. versionchanged: 2016.11.0
            contents_pillar can also be a list, and the pillars will be
            concatinated together to form one file.


        Operates like ``contents``, but draws from a value stored in pillar,
        using the pillar path syntax used in :mod:`pillar.get
        <salt.modules.pillar.get>`. This is useful when the pillar value
        contains newlines, as referencing a pillar variable using a jinja/mako
        template can result in YAML formatting issues due to the newlines
        causing indentation mismatches.

        For example, the following could be used to deploy an SSH private key:

        .. code-block:: yaml

            /home/deployer/.ssh/id_rsa:
              file.managed:
                - user: deployer
                - group: deployer
                - mode: 600
                - attrs: a
                - contents_pillar: userdata:deployer:id_rsa

        This would populate ``/home/deployer/.ssh/id_rsa`` with the contents of
        ``pillar['userdata']['deployer']['id_rsa']``. An example of this pillar
        setup would be like so:

        .. code-block:: yaml

            userdata:
              deployer:
                id_rsa: |
                    -----BEGIN RSA PRIVATE KEY-----
                    MIIEowIBAAKCAQEAoQiwO3JhBquPAalQF9qP1lLZNXVjYMIswrMe2HcWUVBgh+vY
                    U7sCwx/dH6+VvNwmCoqmNnP+8gTPKGl1vgAObJAnMT623dMXjVKwnEagZPRJIxDy
                    B/HaAre9euNiY3LvIzBTWRSeMfT+rWvIKVBpvwlgGrfgz70m0pqxu+UyFbAGLin+
                    GpxzZAMaFpZw4sSbIlRuissXZj/sHpQb8p9M5IeO4Z3rjkCP1cxI
                    -----END RSA PRIVATE KEY-----

        .. note::

            The private key above is shortened to keep the example brief, but
            shows how to do multiline string in YAML. The key is followed by a
            pipe character, and the mutliline string is indented two more
            spaces.

            To avoid the hassle of creating an indented multiline YAML string,
            the :mod:`file_tree external pillar <salt.pillar.file_tree>` can
            be used instead. However, this will not work for binary files in
            Salt releases before 2015.8.4.

    contents_grains
        .. versionadded:: 2014.7.0

        Operates like ``contents``, but draws from a value stored in grains,
        using the grains path syntax used in :mod:`grains.get
        <salt.modules.grains.get>`. This functionality works similarly to
        ``contents_pillar``, but with grains.

        For example, the following could be used to deploy a "message of the day"
        file:

        .. code-block:: yaml

            write_motd:
              file.managed:
                - name: /etc/motd
                - contents_grains: motd

        This would populate ``/etc/motd`` file with the contents of the ``motd``
        grain. The ``motd`` grain is not a default grain, and would need to be
        set prior to running the state:

        .. code-block:: bash

            salt '*' grains.set motd 'Welcome! This system is managed by Salt.'

    contents_newline : True
        .. versionadded:: 2014.7.0
        .. versionchanged:: 2015.8.4
            This option is now ignored if the contents being deployed contain
            binary data.

        If ``True``, files managed using ``contents``, ``contents_pillar``, or
        ``contents_grains`` will have a newline added to the end of the file if
        one is not present. Setting this option to ``False`` will omit this
        final newline.

    contents_delimiter
        .. versionadded:: 2015.8.4

        Can be used to specify an alternate delimiter for ``contents_pillar``
        or ``contents_grains``. This delimiter will be passed through to
        :py:func:`pillar.get <salt.modules.pillar.get>` or :py:func:`grains.get
        <salt.modules.grains.get>` when retrieving the contents.

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

    allow_empty : True
        .. versionadded:: 2015.8.4

        If set to ``False``, then the state will fail if the contents specified
        by ``contents_pillar`` or ``contents_grains`` are empty.

    follow_symlinks : True
        .. versionadded:: 2014.7.0

        If the desired path is a symlink follow it and make changes to the
        file to which the symlink points.

    check_cmd
        .. versionadded:: 2014.7.0

        The specified command will be run with an appended argument of a
        *temporary* file containing the new managed contents.  If the command
        exits with a zero status the new managed contents will be written to
        the managed destination. If the command exits with a nonzero exit
        code, the state will fail and no changes will be made to the file.

        For example, the following could be used to verify sudoers before making
        changes:

        .. code-block:: yaml

            /etc/sudoers:
              file.managed:
                - user: root
                - group: root
                - mode: 0440
                - attrs: i
                - source: salt://sudoers/files/sudoers.jinja
                - template: jinja
                - check_cmd: /usr/sbin/visudo -c -f

        **NOTE**: This ``check_cmd`` functions differently than the requisite
        ``check_cmd``.

    tmp_ext
        Suffix for temp file created by ``check_cmd``. Useful for checkers
        dependent on config file extension (e.g. the init-checkconf upstart
        config checker).

        .. code-block:: yaml

            /etc/init/test.conf:
              file.managed:
                - user: root
                - group: root
                - mode: 0440
                - tmp_ext: '.conf'
                - contents:
                  - 'description "Salt Minion"''
                  - 'start on started mountall'
                  - 'stop on shutdown'
                  - 'respawn'
                  - 'exec salt-minion'
                - check_cmd: init-checkconf -f

    skip_verify : False
        If ``True``, hash verification of remote file sources (``http://``,
        ``https://``, ``ftp://``) will be skipped, and the ``source_hash``
        argument will be ignored.

        .. versionadded:: 2016.3.0

    win_owner : None
        The owner of the directory. If this is not passed, user will be used. If
        user is not passed, the account under which Salt is running will be
        used.

        .. versionadded:: 2017.7.0

    win_perms : None
        A dictionary containing permissions to grant and their propagation. For
        example: ``{'Administrators': {'perms': 'full_control'}}`` Can be a
        single basic perm or a list of advanced perms. ``perms`` must be
        specified. ``applies_to`` does not apply to file objects.

        .. versionadded:: 2017.7.0

    win_deny_perms : None
        A dictionary containing permissions to deny and their propagation. For
        example: ``{'Administrators': {'perms': 'full_control'}}`` Can be a
        single basic perm or a list of advanced perms. ``perms`` must be
        specified. ``applies_to`` does not apply to file objects.

        .. versionadded:: 2017.7.0

    win_inheritance : True
        True to inherit permissions from the parent directory, False not to
        inherit permission.

        .. versionadded:: 2017.7.0

    win_perms_reset : False
        If ``True`` the existing DACL will be cleared and replaced with the
        settings defined in this function. If ``False``, new entries will be
        appended to the existing DACL. Default is ``False``.

        .. versionadded:: 2018.3.0

    Here's an example using the above ``win_*`` parameters:

    .. code-block:: yaml

        create_config_file:
          file.managed:
            - name: C:\config\settings.cfg
            - source: salt://settings.cfg
            - win_owner: Administrators
            - win_perms:
                # Basic Permissions
                dev_ops:
                  perms: full_control
                # List of advanced permissions
                appuser:
                  perms:
                    - read_attributes
                    - read_ea
                    - create_folders
                    - read_permissions
                joe_snuffy:
                  perms: read
            - win_deny_perms:
                fred_snuffy:
                  perms: full_control
            - win_inheritance: False
    '''
    if 'env' in kwargs:
        # "env" is not supported; Use "saltenv".
        kwargs.pop('env')

    name = os.path.expanduser(name)

    ret = {'changes': {},
           'pchanges': {},
           'comment': '',
           'name': name,
           'result': True}

    if not name:
        return _error(ret, 'Destination file name is required')

    if mode is not None and salt.utils.platform.is_windows():
        return _error(ret, 'The \'mode\' option is not supported on Windows')

    if attrs is not None and salt.utils.platform.is_windows():
        return _error(ret, 'The \'attrs\' option is not supported on Windows')

    try:
        keep_mode = mode.lower() == 'keep'
        if keep_mode:
            # We're not hard-coding the mode, so set it to None
            mode = None
    except AttributeError:
        keep_mode = False

    # Make sure that any leading zeros stripped by YAML loader are added back
    mode = salt.utils.files.normalize_mode(mode)

    contents_count = len(
        [x for x in (contents, contents_pillar, contents_grains)
         if x is not None]
    )

    if source and contents_count > 0:
        return _error(
            ret,
            '\'source\' cannot be used in combination with \'contents\', '
            '\'contents_pillar\', or \'contents_grains\''
        )
    elif keep_mode and contents_count > 0:
        return _error(
            ret,
            'Mode preservation cannot be used in combination with \'contents\', '
            '\'contents_pillar\', or \'contents_grains\''
        )
    elif contents_count > 1:
        return _error(
            ret,
            'Only one of \'contents\', \'contents_pillar\', and '
            '\'contents_grains\' is permitted'
        )

    # If no source is specified, set replace to False, as there is nothing
    # with which to replace the file.
    if not source and contents_count == 0 and replace:
        replace = False
        log.warning(
            'State for file: {0} - Neither \'source\' nor \'contents\' nor '
            '\'contents_pillar\' nor \'contents_grains\' was defined, yet '
            '\'replace\' was set to \'True\'. As there is no source to '
            'replace the file with, \'replace\' has been set to \'False\' to '
            'avoid reading the file unnecessarily.'.format(name)
        )

    # Use this below to avoid multiple '\0' checks and save some CPU cycles
    if contents_pillar is not None:
        if isinstance(contents_pillar, list):
            list_contents = []
            for nextp in contents_pillar:
                nextc = __salt__['pillar.get'](nextp, __NOT_FOUND,
                                               delimiter=contents_delimiter)
                if nextc is __NOT_FOUND:
                    return _error(
                        ret,
                        'Pillar {0} does not exist'.format(nextp)
                    )
                list_contents.append(nextc)
            use_contents = os.linesep.join(list_contents)
        else:
            use_contents = __salt__['pillar.get'](contents_pillar, __NOT_FOUND,
                                                  delimiter=contents_delimiter)
            if use_contents is __NOT_FOUND:
                return _error(
                    ret,
                    'Pillar {0} does not exist'.format(contents_pillar)
                )

    elif contents_grains is not None:
        if isinstance(contents_grains, list):
            list_contents = []
            for nextg in contents_grains:
                nextc = __salt__['grains.get'](nextg, __NOT_FOUND,
                                               delimiter=contents_delimiter)
                if nextc is __NOT_FOUND:
                    return _error(
                        ret,
                        'Grain {0} does not exist'.format(nextc)
                    )
                list_contents.append(nextc)
            use_contents = os.linesep.join(list_contents)
        else:
            use_contents = __salt__['grains.get'](contents_grains, __NOT_FOUND,
                                                  delimiter=contents_delimiter)
            if use_contents is __NOT_FOUND:
                return _error(
                    ret,
                    'Grain {0} does not exist'.format(contents_grains)
                )

    elif contents is not None:
        use_contents = contents

    else:
        use_contents = None

    if use_contents is not None:
        if not allow_empty and not use_contents:
            if contents_pillar:
                contents_id = 'contents_pillar {0}'.format(contents_pillar)
            elif contents_grains:
                contents_id = 'contents_grains {0}'.format(contents_grains)
            else:
                contents_id = '\'contents\''
            return _error(
                ret,
                '{0} value would result in empty contents. Set allow_empty '
                'to True to allow the managed file to be empty.'
                .format(contents_id)
            )

        if isinstance(use_contents, bytes) and b'\0' in use_contents:
            contents = use_contents
        elif isinstance(use_contents, six.string_types) and str('\0') in use_contents:
            contents = use_contents
        else:
            validated_contents = _validate_str_list(use_contents)
            if not validated_contents:
                return _error(
                    ret,
                    'Contents specified by contents/contents_pillar/'
                    'contents_grains is not a string or list of strings, and '
                    'is not binary data. SLS is likely malformed.'
                )
            contents = os.linesep.join(validated_contents)
            if contents_newline and not contents.endswith(os.linesep):
                contents += os.linesep
        if template:
            contents = __salt__['file.apply_template_on_contents'](
                contents,
                template=template,
                context=context,
                defaults=defaults,
                saltenv=__env__)
            if not isinstance(contents, six.string_types):
                if 'result' in contents:
                    ret['result'] = contents['result']
                else:
                    ret['result'] = False
                if 'comment' in contents:
                    ret['comment'] = contents['comment']
                else:
                    ret['comment'] = 'Error while applying template on contents'
                return ret

    user = _test_owner(kwargs, user=user)
    if salt.utils.platform.is_windows():

        # If win_owner not passed, use user
        if win_owner is None:
            win_owner = user if user else None

        # Group isn't relevant to Windows, use win_perms/win_deny_perms
        if group is not None:
            log.warning(
                'The group argument for {0} has been ignored as this is '
                'a Windows system. Please use the `win_*` parameters to set '
                'permissions in Windows.'.format(name)
            )
        group = user

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

    if os.path.isdir(name):
        ret['comment'] = 'Specified target {0} is a directory'.format(name)
        ret['result'] = False
        return ret

    if context is None:
        context = {}
    elif not isinstance(context, dict):
        return _error(
            ret, 'Context must be formed as a dict')
    if defaults and not isinstance(defaults, dict):
        return _error(
            ret, 'Defaults must be formed as a dict')

    if not replace and os.path.exists(name):
        # Check and set the permissions if necessary
        if salt.utils.platform.is_windows():
            ret = __salt__['file.check_perms'](
                path=name,
                ret=ret,
                owner=win_owner,
                grant_perms=win_perms,
                deny_perms=win_deny_perms,
                inheritance=win_inheritance,
                reset=win_perms_reset)
        else:
            ret, _ = __salt__['file.check_perms'](
                name, ret, user, group, mode, attrs, follow_symlinks)
        if __opts__['test']:
            ret['comment'] = 'File {0} not updated'.format(name)
        elif not ret['changes'] and ret['result']:
            ret['comment'] = ('File {0} exists with proper permissions. '
                              'No changes made.'.format(name))
        return ret

    accum_data, _ = _load_accumulators()
    if name in accum_data:
        if not context:
            context = {}
        context['accumulator'] = accum_data[name]

    try:
        if __opts__['test']:
            if 'file.check_managed_changes' in __salt__:
                ret['pchanges'] = __salt__['file.check_managed_changes'](
                    name,
                    source,
                    source_hash,
                    source_hash_name,
                    user,
                    group,
                    mode,
                    attrs,
                    template,
                    context,
                    defaults,
                    __env__,
                    contents,
                    skip_verify,
                    keep_mode,
                    **kwargs
                )

                if salt.utils.platform.is_windows():
                    try:
                        ret = __salt__['file.check_perms'](
                            path=name,
                            ret=ret,
                            owner=win_owner,
                            grant_perms=win_perms,
                            deny_perms=win_deny_perms,
                            inheritance=win_inheritance,
                            reset=win_perms_reset)
                    except CommandExecutionError as exc:
                        if exc.strerror.startswith('Path not found'):
                            ret['pchanges'] = '{0} will be created'.format(name)

            if isinstance(ret['pchanges'], tuple):
                ret['result'], ret['comment'] = ret['pchanges']
            elif ret['pchanges']:
                ret['result'] = None
                ret['comment'] = 'The file {0} is set to be changed'.format(name)
                if 'diff' in ret['pchanges'] and not show_changes:
                    ret['pchanges']['diff'] = '<show_changes=False>'
            else:
                ret['result'] = True
                ret['comment'] = 'The file {0} is in the correct state'.format(name)

            return ret

        # If the source is a list then find which file exists
        source, source_hash = __salt__['file.source_list'](
            source,
            source_hash,
            __env__
        )
    except CommandExecutionError as exc:
        ret['result'] = False
        ret['comment'] = 'Unable to manage file: {0}'.format(exc)
        return ret

    # Gather the source file from the server
    try:
        sfn, source_sum, comment_ = __salt__['file.get_managed'](
            name,
            template,
            source,
            source_hash,
            source_hash_name,
            user,
            group,
            mode,
            attrs,
            __env__,
            context,
            defaults,
            skip_verify,
            **kwargs
        )
    except Exception as exc:
        ret['changes'] = {}
        log.debug(traceback.format_exc())
        return _error(ret, 'Unable to manage file: {0}'.format(exc))

    tmp_filename = None

    if check_cmd:
        tmp_filename = salt.utils.files.mkstemp(suffix=tmp_ext)

        # if exists copy existing file to tmp to compare
        if __salt__['file.file_exists'](name):
            try:
                __salt__['file.copy'](name, tmp_filename)
            except Exception as exc:
                return _error(
                    ret,
                    'Unable to copy file {0} to {1}: {2}'.format(
                        name, tmp_filename, exc
                    )
                )

        try:
            ret = __salt__['file.manage_file'](
                tmp_filename,
                sfn,
                ret,
                source,
                source_sum,
                user,
                group,
                mode,
                attrs,
                __env__,
                backup,
                makedirs,
                template,
                show_changes,
                contents,
                dir_mode,
                follow_symlinks,
                skip_verify,
                keep_mode,
                win_owner=win_owner,
                win_perms=win_perms,
                win_deny_perms=win_deny_perms,
                win_inheritance=win_inheritance,
                win_perms_reset=win_perms_reset,
                encoding=encoding,
                encoding_errors=encoding_errors,
                **kwargs)
        except Exception as exc:
            ret['changes'] = {}
            log.debug(traceback.format_exc())
            salt.utils.files.remove(tmp_filename)
            if not keep_source and sfn:
                salt.utils.files.remove(sfn)
            return _error(ret, 'Unable to check_cmd file: {0}'.format(exc))

        # file being updated to verify using check_cmd
        if ret['changes']:
            # Reset ret
            ret = {'changes': {},
                   'comment': '',
                   'name': name,
                   'result': True}

            check_cmd_opts = {}
            if 'shell' in __grains__:
                check_cmd_opts['shell'] = __grains__['shell']

            cret = mod_run_check_cmd(check_cmd, tmp_filename, **check_cmd_opts)
            if isinstance(cret, dict):
                ret.update(cret)
                salt.utils.files.remove(tmp_filename)
                return ret

            # Since we generated a new tempfile and we are not returning here
            # lets change the original sfn to the new tempfile or else we will
            # get file not found

            sfn = tmp_filename

        else:
            ret = {'changes': {},
                   'comment': '',
                   'name': name,
                   'result': True}

    if comment_ and contents is None:
        return _error(ret, comment_)
    else:
        try:
            return __salt__['file.manage_file'](
                name,
                sfn,
                ret,
                source,
                source_sum,
                user,
                group,
                mode,
                attrs,
                __env__,
                backup,
                makedirs,
                template,
                show_changes,
                contents,
                dir_mode,
                follow_symlinks,
                skip_verify,
                keep_mode,
                win_owner=win_owner,
                win_perms=win_perms,
                win_deny_perms=win_deny_perms,
                win_inheritance=win_inheritance,
                win_perms_reset=win_perms_reset,
                encoding=encoding,
                encoding_errors=encoding_errors,
                **kwargs)
        except Exception as exc:
            ret['changes'] = {}
            log.debug(traceback.format_exc())
            return _error(ret, 'Unable to manage file: {0}'.format(exc))
        finally:
            if tmp_filename:
                salt.utils.files.remove(tmp_filename)
            if not keep_source and sfn:
                salt.utils.files.remove(sfn)