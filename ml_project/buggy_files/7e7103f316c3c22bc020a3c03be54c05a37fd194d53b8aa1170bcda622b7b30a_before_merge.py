def _legacy_git_pillar(minion_id, repo_string, pillar_dirs):
    '''
    Support pre-Beryllium config schema
    '''
    if pillar_dirs is None:
        return
    # split the branch, repo name and optional extra (key=val) parameters.
    options = repo_string.strip().split()
    branch_env = options[0]
    repo_location = options[1]
    root = ''

    for extraopt in options[2:]:
        # Support multiple key=val attributes as custom parameters.
        DELIM = '='
        if DELIM not in extraopt:
            log.error('Incorrectly formatted extra parameter. '
                      'Missing \'{0}\': {1}'.format(DELIM, extraopt))
        key, val = _extract_key_val(extraopt, DELIM)
        if key == 'root':
            root = val
        else:
            log.warning('Unrecognized extra parameter: {0}'.format(key))

    # environment is "different" from the branch
    cfg_branch, _, environment = branch_env.partition(':')

    gitpil = _LegacyGitPillar(cfg_branch, repo_location, __opts__)
    branch = gitpil.branch

    if environment == '':
        if branch == 'master':
            environment = 'base'
        else:
            environment = branch

    # normpath is needed to remove appended '/' if root is empty string.
    pillar_dir = os.path.normpath(os.path.join(gitpil.working_dir, root))

    pillar_dirs.setdefault(pillar_dir, {})

    if cfg_branch == '__env__' and branch not in ['master', 'base']:
        gitpil.update()
    elif pillar_dirs[pillar_dir].get(branch, False):
        return {}  # we've already seen this combo

    pillar_dirs[pillar_dir].setdefault(branch, True)

    # Don't recurse forever-- the Pillar object will re-call the ext_pillar
    # function
    if __opts__['pillar_roots'].get(branch, []) == [pillar_dir]:
        return {}

    opts = copy.deepcopy(__opts__)

    opts['pillar_roots'][environment] = [pillar_dir]

    pil = Pillar(opts, __grains__, minion_id, branch)

    return pil.compile_pillar(ext=False)