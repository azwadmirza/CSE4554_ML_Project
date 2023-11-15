def get_root() -> str:
    # Git 2.25 introduced a change to "rev-parse --show-toplevel" that exposed
    # underlying volumes for Windows drives mapped with SUBST.  We use
    # "rev-parse --show-cdup" to get the appropriate path, but must perform
    # an extra check to see if we are in the .git directory.
    try:
        root = os.path.realpath(
            cmd_output('git', 'rev-parse', '--show-cdup')[1].strip(),
        )
        git_dir = os.path.realpath(get_git_dir())
    except CalledProcessError:
        raise FatalError(
            'git failed. Is it installed, and are you in a Git repository '
            'directory?',
        )
    if os.path.samefile(root, git_dir):
        raise FatalError(
            'git toplevel unexpectedly empty! make sure you are not '
            'inside the `.git` directory of your repository.',
        )
    return root