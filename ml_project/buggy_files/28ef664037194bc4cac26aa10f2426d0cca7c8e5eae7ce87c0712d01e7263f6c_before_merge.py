def update_git_repos(opts=None, clean=False, masterless=False):
    '''
    Checkout git repos containing Windows Software Package Definitions

    opts
        Specify an alternate opts dict. Should not be used unless this function
        is imported into an execution module.

    clean : False
        Clean repo cachedirs which are not configured under
        :conf_master:`winrepo_remotes`.

        .. warning::
            This argument should not be set to ``True`` if a mix of git and
            non-git repo definitions are being used, as it will result in the
            non-git repo definitions being removed.

        .. versionadded:: 2015.8.0

    CLI Examples:

    .. code-block:: bash

        salt-run winrepo.update_git_repos
        salt-run winrepo.update_git_repos clean=True
    '''
    if opts is None:
        opts = __opts__

    winrepo_dir = opts['winrepo_dir']
    winrepo_remotes = opts['winrepo_remotes']

    winrepo_cfg = [(winrepo_remotes, winrepo_dir),
                   (opts['winrepo_remotes_ng'], opts['winrepo_dir_ng'])]

    ret = {}
    for remotes, base_dir in winrepo_cfg:
        if not any((salt.utils.gitfs.HAS_GITPYTHON, salt.utils.gitfs.HAS_PYGIT2)):
            # Use legacy code
            winrepo_result = {}
            for remote_info in remotes:
                if '/' in remote_info:
                    targetname = remote_info.split('/')[-1]
                else:
                    targetname = remote_info
                rev = 'HEAD'
                # If a revision is specified, use it.
                try:
                    rev, remote_url = remote_info.strip().split()
                except ValueError:
                    remote_url = remote_info
                gittarget = os.path.join(base_dir, targetname).replace('.', '_')
                if masterless:
                    result = __salt__['state.single']('git.latest',
                                                      name=remote_url,
                                                      rev=rev,
                                                      branch='winrepo',
                                                      target=gittarget,
                                                      force_checkout=True,
                                                      force_reset=True)
                    if isinstance(result, list):
                        # Errors were detected
                        raise CommandExecutionError(
                            'Failed up update winrepo remotes: {0}'.format(
                                '\n'.join(result)
                            )
                        )
                    if 'name' not in result:
                        # Highstate output dict, the results are actually nested
                        # one level down.
                        key = next(iter(result))
                        result = result[key]
                else:
                    mminion = salt.minion.MasterMinion(opts)
                    result = mminion.states['git.latest'](remote_url,
                                                          rev=rev,
                                                          branch='winrepo',
                                                          target=gittarget,
                                                          force_checkout=True,
                                                          force_reset=True)
                winrepo_result[result['name']] = result['result']
            ret.update(winrepo_result)
        else:
            # New winrepo code utilizing salt.utils.gitfs
            try:
                winrepo = salt.utils.gitfs.WinRepo(
                    opts,
                    remotes,
                    per_remote_overrides=PER_REMOTE_OVERRIDES,
                    per_remote_only=PER_REMOTE_ONLY,
                    cache_root=base_dir)
                winrepo.fetch_remotes()
                # Since we're not running update(), we need to manually call
                # clear_old_remotes() to remove directories from remotes that
                # have been removed from configuration.
                if clean:
                    winrepo.clear_old_remotes()
                winrepo.checkout()
            except Exception as exc:
                msg = 'Failed to update winrepo_remotes: {0}'.format(exc)
                log.error(msg, exc_info_on_loglevel=logging.DEBUG)
                return msg
            ret.update(winrepo.winrepo_dirs)
    return ret