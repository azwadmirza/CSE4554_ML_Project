def get_staged_files(cwd=None):
    return zsplit(cmd_output(
        'git', 'diff', '--staged', '--name-only', '--no-ext-diff', '-z',
        # Everything except for D
        '--diff-filter=ACMRTUXB',
        cwd=cwd,
    )[1])