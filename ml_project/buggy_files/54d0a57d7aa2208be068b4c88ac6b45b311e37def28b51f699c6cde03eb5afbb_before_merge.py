def __ls_remote__(name, branch):
    '''
    Returns the upstream hash for any given URL and branch.
    '''
    cmd = "git ls-remote -h " + name + " " + branch + " | cut -f 1"
    return __salt__['cmd.run_stdout'](cmd)