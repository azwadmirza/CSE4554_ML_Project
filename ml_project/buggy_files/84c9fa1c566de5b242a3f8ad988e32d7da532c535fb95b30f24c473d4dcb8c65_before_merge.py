def ext_pillar(minion_id, repo, pillar_dirs):
    '''
    Checkout the ext_pillar sources and compile the resulting pillar SLS
    '''
    if isinstance(repo, six.string_types):
        return _legacy_git_pillar(minion_id, repo, pillar_dirs)
    else:
        opts = copy.deepcopy(__opts__)
        opts['pillar_roots'] = {}
        pillar = salt.utils.gitfs.GitPillar(opts)
        pillar.init_remotes(repo, PER_REMOTE_OVERRIDES)
        pillar.checkout()
        ret = {}
        merge_strategy = __opts__.get(
            'pillar_source_merging_strategy',
            'smart'
        )
        merge_lists = __opts__.get(
            'pillar_merge_lists',
            False
        )
        for pillar_dir, env in six.iteritems(pillar.pillar_dirs):
            log.debug(
                'git_pillar is processing pillar SLS from {0} for pillar '
                'env \'{1}\''.format(pillar_dir, env)
            )
            all_dirs = [d for (d, e) in six.iteritems(pillar.pillar_dirs)
                        if env == e]

            # Ensure that the current pillar_dir is first in the list, so that
            # the pillar top.sls is sourced from the correct location.
            pillar_roots = [pillar_dir]
            pillar_roots.extend([x for x in all_dirs if x != pillar_dir])
            opts['pillar_roots'] = {env: pillar_roots}

            local_pillar = Pillar(opts, __grains__, minion_id, env)
            ret = salt.utils.dictupdate.merge(
                ret,
                local_pillar.compile_pillar(ext=False),
                strategy=merge_strategy,
                merge_lists=merge_lists
            )
        return ret