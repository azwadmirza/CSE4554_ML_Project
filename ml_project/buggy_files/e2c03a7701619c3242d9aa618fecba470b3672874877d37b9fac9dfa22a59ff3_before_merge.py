def recurse(name,
            source,
            clean=False,
            require=None,
            user=None,
            group=None,
            dir_mode=None,
            file_mode=None,
            sym_mode=None,
            template=None,
            context=None,
            defaults=None,
            env=None,
            include_empty=False,
            backup='',
            include_pat=None,
            exclude_pat=None,
            maxdepth=None,
            keep_symlinks=False,
            force_symlinks=False,
            **kwargs):
    '''
    Recurse through a subdirectory on the master and copy said subdirectory
    over to the specified path.

    name
        The directory to set the recursion in

    source
        The source directory, this directory is located on the salt master file
        server and is specified with the salt:// protocol. If the directory is
        located on the master in the directory named spam, and is called eggs,
        the source string is salt://spam/eggs

    clean
        Make sure that only files that are set up by salt and required by this
        function are kept. If this option is set then everything in this
        directory will be deleted unless it is required.

    require
        Require other resources such as packages or files

    user
        The user to own the directory. This defaults to the user salt is
        running as on the minion

    group
        The group ownership set for the directory. This defaults to the group
        salt is running as on the minion. On Windows, this is ignored

    dir_mode
        The permissions mode to set on any directories created. Not supported on
        Windows

    file_mode
        The permissions mode to set on any files created. Not supported on
        Windows

    sym_mode
        The permissions mode to set on any symlink created. Not supported on
        Windows

    template
        If this setting is applied then the named templating engine will be
        used to render the downloaded file. Supported templates are:
        `jinja`, `mako` and `wempy`.

    .. note::

        The template option is required when recursively applying templates.

    context
        Overrides default context variables passed to the template.

    defaults
        Default context passed to the template.

    include_empty
        Set this to True if empty directories should also be created
        (default is False)

    include_pat
        When copying, include only this pattern from the source. Default
        is glob match; if prefixed with 'E@', then regexp match.
        Example:

        .. code-block:: yaml

          - include_pat: hello*       :: glob matches 'hello01', 'hello02'
                                         ... but not 'otherhello'
          - include_pat: E@hello      :: regexp matches 'otherhello',
                                         'hello01' ...

    exclude_pat
        Exclude this pattern from the source when copying. If both
        `include_pat` and `exclude_pat` are supplied, then it will apply
        conditions cumulatively. i.e. first select based on include_pat, and
        then within that result apply exclude_pat.

        Also, when 'clean=True', exclude this pattern from the removal
        list and preserve in the destination.
        Example:

        .. code-block:: yaml

          - exclude_pat: APPDATA*               :: glob matches APPDATA.01,
                                                   APPDATA.02,.. for exclusion
          - exclude_pat: E@(APPDATA)|(TEMPDATA) :: regexp matches APPDATA
                                                   or TEMPDATA for exclusion

    maxdepth
        When copying, only copy paths which are of depth `maxdepth` from the
        source path.
        Example:

        .. code-block:: yaml

          - maxdepth: 0      :: Only include files located in the source
                                directory
          - maxdepth: 1      :: Only include files located in the source
                                or immediate subdirectories

    keep_symlinks
        Keep symlinks when copying from the source. This option will cause
        the copy operation to terminate at the symlink. If desire behavior
        similar to rsync, then set this to True.

    force_symlinks
        Force symlink creation. This option will force the symlink creation.
        If a file or directory is obstructing symlink creation it will be
        recursively removed so that symlink creation can proceed. This
        option is usually not needed except in special circumstances.
    '''
    name = os.path.expanduser(name)

    user = _test_owner(kwargs, user=user)
    if salt.utils.is_windows():
        if group is not None:
            log.warning(
                'The group argument for {0} has been ignored as this '
                'is a Windows system.'.format(name)
            )
        group = user
    ret = {
        'name': name,
        'changes': {},
        'result': True,
        'comment': {}  # { path: [comment, ...] }
    }

    if 'mode' in kwargs:
        ret['result'] = False
        ret['comment'] = (
            '\'mode\' is not allowed in \'file.recurse\'. Please use '
            '\'file_mode\' and \'dir_mode\'.'
        )
        return ret

    # Make sure that leading zeros stripped by YAML loader are added back
    dir_mode = __salt__['config.manage_mode'](dir_mode)
    file_mode = __salt__['config.manage_mode'](file_mode)

    u_check = _check_user(user, group)
    if u_check:
        # The specified user or group do not exist
        return _error(ret, u_check)
    if not os.path.isabs(name):
        return _error(
            ret, 'Specified file {0} is not an absolute path'.format(name))

    if isinstance(env, string_types):
        msg = (
            'Passing a salt environment should be done using \'saltenv\' not '
            '\'env\'. This warning will go away in Salt Boron and this '
            'will be the default and expected behavior. Please update your '
            'state files.'
        )
        salt.utils.warn_until('Boron', msg)
        ret.setdefault('warnings', []).append(msg)
        # No need to set __env__ = env since that's done in the state machinery

    # expand source into source_list
    source_list = _validate_str_list(source)

    for idx, val in enumerate(source_list):
        source_list[idx] = val.rstrip('/')

    for precheck in source_list:
        if not precheck.startswith('salt://'):
            return _error(ret, ('Invalid source {0!r} '
                                '(must be a salt:// URI)'.format(precheck)))

    # Select the first source in source_list that exists
    try:
        source, source_hash = __salt__['file.source_list'](source_list, '', __env__)
    except CommandExecutionError as exc:
        ret['result'] = False
        ret['comment'] = 'Recurse failed: {0}'.format(exc)
        return ret

    # Check source path relative to fileserver root, make sure it is a
    # directory
    source_rel = source.partition('://')[2]
    master_dirs = __salt__['cp.list_master_dirs'](__env__)
    if source_rel not in master_dirs \
            and not any((x for x in master_dirs
                         if x.startswith(source_rel + '/'))):
        ret['result'] = False
        ret['comment'] = (
            'The directory {0!r} does not exist on the salt fileserver '
            'in saltenv {1!r}'.format(source, __env__)
        )
        return ret

    # Verify the target directory
    if not os.path.isdir(name):
        if os.path.exists(name):
            # it is not a dir, but it exists - fail out
            return _error(
                ret, 'The path {0} exists and is not a directory'.format(name))
        if not __opts__['test']:
            __salt__['file.makedirs_perms'](
                name, user, group, int(str(dir_mode), 8) if dir_mode else None)

    def add_comment(path, comment):
        comments = ret['comment'].setdefault(path, [])
        if isinstance(comment, string_types):
            comments.append(comment)
        else:
            comments.extend(comment)

    def merge_ret(path, _ret):
        # Use the most "negative" result code (out of True, None, False)
        if _ret['result'] is False or ret['result'] is True:
            ret['result'] = _ret['result']

        # Only include comments about files that changed
        if _ret['result'] is not True and _ret['comment']:
            add_comment(path, _ret['comment'])

        if _ret['changes']:
            ret['changes'][path] = _ret['changes']

    def manage_file(path, source):
        source = u'{0}|{1}'.format(source[:7], source[7:])
        if clean and os.path.exists(path) and os.path.isdir(path):
            _ret = {'name': name, 'changes': {}, 'result': True, 'comment': ''}
            if __opts__['test']:
                _ret['comment'] = 'Replacing directory {0} with a ' \
                                  'file'.format(path)
                _ret['result'] = None
                merge_ret(path, _ret)
                return
            else:
                shutil.rmtree(path)
                _ret['changes'] = {'diff': 'Replaced directory with a '
                                           'new file'}
                merge_ret(path, _ret)

        # Conflicts can occur if some kwargs are passed in here
        pass_kwargs = {}
        faults = ['mode', 'makedirs']
        for key in kwargs:
            if key not in faults:
                pass_kwargs[key] = kwargs[key]

        _ret = managed(
            path,
            source=source,
            user=user,
            group=group,
            mode=file_mode,
            template=template,
            makedirs=True,
            context=context,
            defaults=defaults,
            backup=backup,
            **pass_kwargs)
        merge_ret(path, _ret)

    def manage_directory(path):
        if os.path.basename(path) == '..':
            return
        if clean and os.path.exists(path) and not os.path.isdir(path):
            _ret = {'name': name, 'changes': {}, 'result': True, 'comment': ''}
            if __opts__['test']:
                _ret['comment'] = 'Replacing {0} with a directory'.format(path)
                _ret['result'] = None
                merge_ret(path, _ret)
                return
            else:
                os.remove(path)
                _ret['changes'] = {'diff': 'Replaced file with a directory'}
                merge_ret(path, _ret)

        _ret = directory(
            path,
            user=user,
            group=group,
            recurse=[],
            dir_mode=dir_mode,
            file_mode=None,
            makedirs=True,
            clean=False,
            require=None)
        merge_ret(path, _ret)

    # Process symlinks and return the updated filenames list
    def process_symlinks(filenames, symlinks):
        for lname, ltarget in symlinks.items():
            if not salt.utils.check_include_exclude(
                    os.path.relpath(lname, srcpath), include_pat, exclude_pat):
                continue
            srelpath = os.path.relpath(lname, srcpath)
            # Check for max depth
            if maxdepth is not None:
                srelpieces = srelpath.split('/')
                if not srelpieces[-1]:
                    srelpieces = srelpieces[:-1]
                if len(srelpieces) > maxdepth + 1:
                    continue
            # Check for all paths that begin with the symlink
            # and axe it leaving only the dirs/files below it.
            # This needs to use list() otherwise they reference
            # the same list.
            _filenames = list(filenames)
            for filename in _filenames:
                if filename.startswith(lname):
                    log.debug('** skipping file ** {0}, it intersects a '
                              'symlink'.format(filename))
                    filenames.remove(filename)
            # Create the symlink along with the necessary dirs.
            # The dir perms/ownership will be adjusted later
            # if needed
            _ret = symlink(os.path.join(name, srelpath),
                           ltarget,
                           makedirs=True,
                           force=force_symlinks,
                           user=user,
                           group=group,
                           mode=sym_mode)
            if not _ret:
                continue
            merge_ret(os.path.join(name, srelpath), _ret)
            # Add the path to the keep set in case clean is set to True
            keep.add(os.path.join(name, srelpath))
        vdir.update(keep)
        return filenames

    keep = set()
    vdir = set()
    srcpath = source[7:]
    if not srcpath.endswith('/'):
        # we're searching for things that start with this *directory*.
        # use '/' since #master only runs on POSIX
        srcpath = srcpath + '/'
    fns_ = __salt__['cp.list_master'](__env__, srcpath)
    # If we are instructed to keep symlinks, then process them.
    if keep_symlinks:
        # Make this global so that emptydirs can use it if needed.
        symlinks = __salt__['cp.list_master_symlinks'](__env__, srcpath)
        fns_ = process_symlinks(fns_, symlinks)
    for fn_ in fns_:
        if not fn_.strip():
            continue

        # fn_ here is the absolute (from file_roots) source path of
        # the file to copy from; it is either a normal file or an
        # empty dir(if include_empty==true).

        relname = os.path.relpath(fn_, srcpath)
        if relname.startswith('..'):
            continue

        # Check for maxdepth of the relative path
        if maxdepth is not None:
            # Since paths are all master, just use POSIX separator
            relpieces = relname.split('/')
            # Handle empty directories (include_empty==true) by removing the
            # the last piece if it is an empty string
            if not relpieces[-1]:
                relpieces = relpieces[:-1]
            if len(relpieces) > maxdepth + 1:
                continue

        # - Check if it is to be excluded. Match only part of the path
        # relative to the target directory
        if not salt.utils.check_include_exclude(
                relname, include_pat, exclude_pat):
            continue
        dest = os.path.join(name, relname)
        dirname = os.path.dirname(dest)
        keep.add(dest)

        if dirname not in vdir:
            # verify the directory perms if they are set
            manage_directory(dirname)
            vdir.add(dirname)

        src = u'salt://{0}'.format(fn_)
        manage_file(dest, src)

    if include_empty:
        mdirs = __salt__['cp.list_master_dirs'](__env__, srcpath)
        for mdir in mdirs:
            if not salt.utils.check_include_exclude(
                    os.path.relpath(mdir, srcpath), include_pat, exclude_pat):
                continue
            mdest = os.path.join(name, os.path.relpath(mdir, srcpath))
            # Check for symlinks that happen to point to an empty dir.
            if keep_symlinks:
                islink = False
                for link in symlinks:
                    if mdir.startswith(link, 0):
                        log.debug('** skipping empty dir ** {0}, it intersects'
                                  ' a symlink'.format(mdir))
                        islink = True
                        break
                if islink:
                    continue

            manage_directory(mdest)
            keep.add(mdest)

    keep = list(keep)
    if clean:
        # TODO: Use directory(clean=True) instead
        keep += _gen_keep_files(name, require)
        removed = _clean_dir(name, list(keep), exclude_pat)
        if removed:
            if __opts__['test']:
                if ret['result']:
                    ret['result'] = None
                add_comment('removed', removed)
            else:
                ret['changes']['removed'] = removed

    # Flatten comments until salt command line client learns
    # to display structured comments in a readable fashion
    ret['comment'] = '\n'.join(u'\n#### {0} ####\n{1}'.format(
        k, v if isinstance(v, string_types) else '\n'.join(v)
    ) for (k, v) in six.iteritems(ret['comment'])).strip()

    if not ret['comment']:
        ret['comment'] = 'Recursively updated {0}'.format(name)

    if not ret['changes'] and ret['result']:
        ret['comment'] = 'The directory {0} is in the correct state'.format(
            name
        )

    return ret