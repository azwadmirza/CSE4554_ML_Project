def _checkout(cwd, repo, branch):
    logger.debug('  Checking out branch {}.'.format(branch))

    run_cmd(cwd, ['git', 'remote', 'set-branches', 'origin', branch])
    run_cmd(cwd, ['git', 'fetch', '--tags', '--depth', '1', 'origin', branch])

    tags = list_tags(cwd)

    # Prefer tags to branches if one exists
    if branch in tags:
        spec = 'tags/{}'.format(branch)
    else:
        spec = 'origin/{}'.format(branch)

    out, err = run_cmd(cwd, ['git', 'reset', '--hard', spec])
    return out, err