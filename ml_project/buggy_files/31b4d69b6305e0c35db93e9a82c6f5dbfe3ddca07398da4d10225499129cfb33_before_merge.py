def get_staged_files():
    return zsplit(cmd_output(
        'git', 'diff', '--staged', '--name-only', '--no-ext-diff', '-z',
        # Everything except for D
        '--diff-filter=ACMRTUXB',
    )[1])