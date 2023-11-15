def clone(repo, cwd, dirname=None, remove_git_dir=False):
    clone_cmd = ['git', 'clone', '--depth', '1', repo]

    if dirname is not None:
        clone_cmd.append(dirname)

    result = run_cmd(cwd, clone_cmd)

    if remove_git_dir:
        rmdir(os.path.join(dirname, '.git'))

    return result