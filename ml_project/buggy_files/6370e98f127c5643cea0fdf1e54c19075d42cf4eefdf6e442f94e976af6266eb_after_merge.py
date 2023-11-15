def _repo_ref(tmpdir, repo, ref):
    # if `ref` is explicitly passed, use it
    if ref:
        return repo, ref

    ref = git.head_rev(repo)
    # if it exists on disk, we'll try and clone it with the local changes
    if os.path.exists(repo) and git.has_diff('HEAD', repo=repo):
        logger.warning('Creating temporary repo with uncommitted changes...')

        shadow = os.path.join(tmpdir, 'shadow-repo')
        cmd_output('git', 'clone', repo, shadow)
        cmd_output('git', 'checkout', ref, '-b', '_pc_tmp', cwd=shadow)

        idx = git.git_path('index', repo=shadow)
        objs = git.git_path('objects', repo=shadow)
        env = dict(os.environ, GIT_INDEX_FILE=idx, GIT_OBJECT_DIRECTORY=objs)

        staged_files = git.get_staged_files(cwd=repo)
        if staged_files:
            xargs(('git', 'add', '--'), staged_files, cwd=repo, env=env)

        cmd_output('git', 'add', '-u', cwd=repo, env=env)
        git.commit(repo=shadow)

        return shadow, git.head_rev(shadow)
    else:
        return repo, ref