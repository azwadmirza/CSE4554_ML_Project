def remove_remote(cwd):
    return run_cmd(cwd, ['git', 'remote', 'rm', 'origin'])