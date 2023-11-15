def detached(name,
           rev,
           target=None,
           remote='origin',
           user=None,
           password=None,
           force_clone=False,
           force_checkout=False,
           fetch_remote=True,
           hard_reset=False,
           submodules=False,
           identity=None,
           https_user=None,
           https_pass=None,
           onlyif=None,
           unless=None,
           output_encoding=None,
           **kwargs):
    '''
    .. versionadded:: 2016.3.0

    Make sure a repository is cloned to the given target directory and is
    a detached HEAD checkout of the commit ID resolved from ``rev``.

    name
        Address of the remote repository.

    rev
        The branch, tag, or commit ID to checkout after clone.
        If a branch or tag is specified it will be resolved to a commit ID
        and checked out.

    ref
        .. deprecated:: 2017.7.0
            Use ``rev`` instead.

    target
        Name of the target directory where repository is about to be cloned.

    remote : origin
        Git remote to use. If this state needs to clone the repo, it will clone
        it using this value as the initial remote name. If the repository
        already exists, and a remote by this name is not present, one will be
        added.

    user
        User under which to run git commands. By default, commands are run by
        the user under which the minion is running.

    password
        Windows only. Required when specifying ``user``. This parameter will be
        ignored on non-Windows platforms.

      .. versionadded:: 2016.3.4

    force_clone : False
        If the ``target`` directory exists and is not a git repository, then
        this state will fail. Set this argument to ``True`` to remove the
        contents of the target directory and clone the repo into it.

    force_checkout : False
        When checking out the revision ID, the state will fail if there are
        unwritten changes. Set this argument to ``True`` to discard unwritten
        changes when checking out.

    fetch_remote : True
        If ``False`` a fetch will not be performed and only local refs
        will be reachable.

    hard_reset : False
        If ``True`` a hard reset will be performed before the checkout and any
        uncommitted modifications to the working directory will be discarded.
        Untracked files will remain in place.

        .. note::
            Changes resulting from a hard reset will not trigger requisites.

    submodules : False
        Update submodules

    identity
        A path on the minion (or a SaltStack fileserver URL, e.g.
        ``salt://path/to/identity_file``) to a private key to use for SSH
        authentication.

    https_user
        HTTP Basic Auth username for HTTPS (only) clones

    https_pass
        HTTP Basic Auth password for HTTPS (only) clones

    onlyif
        A command to run as a check, run the named command only if the command
        passed to the ``onlyif`` option returns true

    unless
        A command to run as a check, only run the named command if the command
        passed to the ``unless`` option returns false

    output_encoding
        Use this option to specify which encoding to use to decode the output
        from any git commands which are run. This should not be needed in most
        cases.

        .. note::
            This should only be needed if the files in the repository were
            created with filenames using an encoding other than UTF-8 to handle
            Unicode characters.

        .. versionadded:: 2018.3.1
    '''

    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    ref = kwargs.pop('ref', None)
    kwargs = salt.utils.args.clean_kwargs(**kwargs)
    if kwargs:
        return _fail(
            ret,
            salt.utils.args.invalid_kwargs(kwargs, raise_exc=False)
        )

    if ref is not None:
        rev = ref
        deprecation_msg = (
            'The \'ref\' argument has been renamed to \'rev\' for '
            'consistency. Please update your SLS to reflect this.'
        )
        ret.setdefault('warnings', []).append(deprecation_msg)
        salt.utils.versions.warn_until('Fluorine', deprecation_msg)

    if not rev:
        return _fail(
            ret,
            '\'{0}\' is not a valid value for the \'rev\' argument'.format(rev)
        )

    if not target:
        return _fail(
            ret,
            '\'{0}\' is not a valid value for the \'target\' argument'.format(rev)
        )

    # Ensure that certain arguments are strings to ensure that comparisons work
    if not isinstance(rev, six.string_types):
        rev = six.text_type(rev)
    if target is not None:
        if not isinstance(target, six.string_types):
            target = six.text_type(target)
        if not os.path.isabs(target):
            return _fail(
                ret,
                'Target \'{0}\' is not an absolute path'.format(target)
            )
    if user is not None and not isinstance(user, six.string_types):
        user = six.text_type(user)
    if remote is not None and not isinstance(remote, six.string_types):
        remote = six.text_type(remote)
    if identity is not None:
        if isinstance(identity, six.string_types):
            identity = [identity]
        elif not isinstance(identity, list):
            return _fail(ret, 'Identity must be either a list or a string')
        for ident_path in identity:
            if 'salt://' in ident_path:
                try:
                    ident_path = __salt__['cp.cache_file'](ident_path)
                except IOError as exc:
                    log.error('Failed to cache %s: %s', ident_path, exc)
                    return _fail(
                        ret,
                        'Identity \'{0}\' does not exist.'.format(
                            ident_path
                        )
                    )
            if not os.path.isabs(ident_path):
                return _fail(
                    ret,
                    'Identity \'{0}\' is not an absolute path'.format(
                        ident_path
                    )
                )
    if https_user is not None and not isinstance(https_user, six.string_types):
        https_user = six.text_type(https_user)
    if https_pass is not None and not isinstance(https_pass, six.string_types):
        https_pass = six.text_type(https_pass)

    if os.path.isfile(target):
        return _fail(
            ret,
            'Target \'{0}\' exists and is a regular file, cannot proceed'
            .format(target)
        )

    try:
        desired_fetch_url = salt.utils.url.add_http_basic_auth(
            name,
            https_user,
            https_pass,
            https_only=True
        )
    except ValueError as exc:
        return _fail(ret, exc.__str__())

    redacted_fetch_url = salt.utils.url.redact_http_basic_auth(desired_fetch_url)

    # Check if onlyif or unless conditions match
    run_check_cmd_kwargs = {'runas': user}
    if 'shell' in __grains__:
        run_check_cmd_kwargs['shell'] = __grains__['shell']
    cret = mod_run_check(
        run_check_cmd_kwargs, onlyif, unless
    )
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    # Determine if supplied ref is a hash
    remote_rev_type = 'ref'
    if len(rev) <= 40 \
            and all(x in string.hexdigits for x in rev):
        rev = rev.lower()
        remote_rev_type = 'hash'

    comments = []
    hash_exists_locally = False
    local_commit_id = None

    gitdir = os.path.join(target, '.git')
    if os.path.isdir(gitdir) \
            or __salt__['git.is_worktree'](target,
                                           user=user,
                                           password=password,
                                           output_encoding=output_encoding):
        # Target directory is a git repository or git worktree

        local_commit_id = _get_local_rev_and_branch(
            target,
            user,
            password,
            output_encoding=output_encoding)[0]

        if remote_rev_type is 'hash':
            try:
                __salt__['git.describe'](target,
                                         rev,
                                         user=user,
                                         password=password,
                                         ignore_retcode=True,
                                         output_encoding=output_encoding)
            except CommandExecutionError:
                hash_exists_locally = False
            else:
                # The rev is a hash and it exists locally so skip to checkout
                hash_exists_locally = True
        else:
            # Check that remote is present and set to correct url
            remotes = __salt__['git.remotes'](target,
                                              user=user,
                                              password=password,
                                              redact_auth=False,
                                              output_encoding=output_encoding)

            if remote in remotes and name in remotes[remote]['fetch']:
                pass
            else:
                # The fetch_url for the desired remote does not match the
                # specified URL (or the remote does not exist), so set the
                # remote URL.
                current_fetch_url = None
                if remote in remotes:
                    current_fetch_url = remotes[remote]['fetch']

                if __opts__['test']:
                    return _neutral_test(
                        ret,
                        'Remote {0} would be set to {1}'.format(
                            remote, name
                        )
                    )

                __salt__['git.remote_set'](target,
                                           url=name,
                                           remote=remote,
                                           user=user,
                                           password=password,
                                           https_user=https_user,
                                           https_pass=https_pass,
                                           output_encoding=output_encoding)
                comments.append(
                    'Remote {0} updated from \'{1}\' to \'{2}\''.format(
                        remote,
                        current_fetch_url,
                        name
                    )
                )

    else:
        # Clone repository
        if os.path.isdir(target):
            target_contents = os.listdir(target)
            if force_clone:
                # Clone is required, and target directory exists, but the
                # ``force`` option is enabled, so we need to clear out its
                # contents to proceed.
                if __opts__['test']:
                    return _neutral_test(
                        ret,
                        'Target directory {0} exists. Since force_clone=True, '
                        'the contents of {0} would be deleted, and {1} would '
                        'be cloned into this directory.'.format(target, name)
                    )
                log.debug(
                    'Removing contents of %s to clone repository %s in its '
                    'place (force_clone=True set in git.detached state)',
                    target, name
                )
                removal_errors = {}
                for target_object in target_contents:
                    target_path = os.path.join(target, target_object)
                    try:
                        salt.utils.files.rm_rf(target_path)
                    except OSError as exc:
                        if exc.errno != errno.ENOENT:
                            removal_errors[target_path] = exc
                if removal_errors:
                    err_strings = [
                        '  {0}\n    {1}'.format(k, v)
                        for k, v in six.iteritems(removal_errors)
                    ]
                    return _fail(
                        ret,
                        'Unable to remove\n{0}'.format('\n'.join(err_strings)),
                        comments
                    )
                ret['changes']['forced clone'] = True
            elif target_contents:
                # Clone is required, but target dir exists and is non-empty. We
                # can't proceed.
                return _fail(
                    ret,
                    'Target \'{0}\' exists, is non-empty and is not a git '
                    'repository. Set the \'force_clone\' option to True to '
                    'remove this directory\'s contents and proceed with '
                    'cloning the remote repository'.format(target)
                )

        log.debug('Target %s is not found, \'git clone\' is required', target)
        if __opts__['test']:
            return _neutral_test(
                ret,
                'Repository {0} would be cloned to {1}'.format(
                    name, target
                )
            )
        try:
            clone_opts = ['--no-checkout']
            if remote != 'origin':
                clone_opts.extend(['--origin', remote])

            __salt__['git.clone'](target,
                                  name,
                                  user=user,
                                  password=password,
                                  opts=clone_opts,
                                  identity=identity,
                                  https_user=https_user,
                                  https_pass=https_pass,
                                  saltenv=__env__,
                                  output_encoding=output_encoding)
            comments.append('{0} cloned to {1}'.format(name, target))

        except Exception as exc:
            log.error(
                'Unexpected exception in git.detached state',
                exc_info=True
            )
            if isinstance(exc, CommandExecutionError):
                msg = _strip_exc(exc)
            else:
                msg = six.text_type(exc)
            return _fail(ret, msg, comments)

    # Repository exists and is ready for fetch/checkout
    refspecs = [
        'refs/heads/*:refs/remotes/{0}/*'.format(remote),
        '+refs/tags/*:refs/tags/*'
    ]
    if hash_exists_locally or fetch_remote is False:
        pass
    else:
        # Fetch refs from remote
        if __opts__['test']:
            return _neutral_test(
                ret,
                'Repository remote {0} would be fetched'.format(remote)
            )
        try:
            fetch_changes = __salt__['git.fetch'](
                target,
                remote=remote,
                force=True,
                refspecs=refspecs,
                user=user,
                password=password,
                identity=identity,
                saltenv=__env__,
                output_encoding=output_encoding)
        except CommandExecutionError as exc:
            msg = 'Fetch failed'
            msg += ':\n\n' + six.text_type(exc)
            return _fail(ret, msg, comments)
        else:
            if fetch_changes:
                comments.append(
                    'Remote {0} was fetched, resulting in updated '
                    'refs'.format(remote)
                )

    #get refs and checkout
    checkout_commit_id = ''
    if remote_rev_type is 'hash':
        if __salt__['git.describe'](
                target,
                rev,
                user=user,
                password=password,
                output_encoding=output_encoding):
            checkout_commit_id = rev
        else:
            return _fail(
                ret,
                'Revision \'{0}\' does not exist'.format(rev)
            )
    else:
        try:
            all_remote_refs = __salt__['git.remote_refs'](
                target,
                user=user,
                password=password,
                identity=identity,
                https_user=https_user,
                https_pass=https_pass,
                ignore_retcode=False,
                output_encoding=output_encoding)

            if 'refs/remotes/'+remote+'/'+rev in all_remote_refs:
                checkout_commit_id = all_remote_refs['refs/remotes/' + remote + '/' + rev]
            elif 'refs/tags/' + rev in all_remote_refs:
                checkout_commit_id = all_remote_refs['refs/tags/' + rev]
            else:
                return _fail(
                    ret,
                    'Revision \'{0}\' does not exist'.format(rev)
                )

        except CommandExecutionError as exc:
            return _fail(
                ret,
                'Failed to list refs for {0}: {1}'.format(remote, _strip_exc(exc))
            )

    if hard_reset:
        if __opts__['test']:
            return _neutral_test(
                ret,
                'Hard reset to HEAD would be performed on {0}'.format(target)
            )
        __salt__['git.reset'](
            target,
            opts=['--hard', 'HEAD'],
            user=user,
            password=password,
            output_encoding=output_encoding)
        comments.append(
            'Repository was reset to HEAD before checking out revision'
        )

    # TODO: implement clean function for git module and add clean flag

    if checkout_commit_id == local_commit_id:
        new_rev = None
    else:
        if __opts__['test']:
            ret['changes']['HEAD'] = {'old': local_commit_id, 'new': checkout_commit_id}
            return _neutral_test(
                ret,
                'Commit ID {0} would be checked out at {1}'.format(
                    checkout_commit_id,
                    target
                )
            )
        __salt__['git.checkout'](target,
                                 checkout_commit_id,
                                 force=force_checkout,
                                 user=user,
                                 password=password,
                                 output_encoding=output_encoding)
        comments.append(
            'Commit ID {0} was checked out at {1}'.format(
                checkout_commit_id,
                target
            )
        )

        try:
            new_rev = __salt__['git.revision'](
                cwd=target,
                user=user,
                password=password,
                ignore_retcode=True,
                output_encoding=output_encoding)
        except CommandExecutionError:
            new_rev = None

    if submodules:
        __salt__['git.submodule'](target,
                                  'update',
                                  opts=['--init', '--recursive'],
                                  user=user,
                                  password=password,
                                  identity=identity,
                                  output_encoding=output_encoding)
        comments.append(
            'Submodules were updated'
        )

    if new_rev is not None:
        ret['changes']['HEAD'] = {'old': local_commit_id, 'new': new_rev}
    else:
        comments.append("Already checked out at correct revision")

    msg = _format_comments(comments)
    log.info(msg)
    ret['comment'] = msg

    return ret