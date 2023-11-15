def get_git_toplevel(path):
    '''Given a path, return the absolute path to the top level directory if it
    is in a git repository. Empty string will be returned if not.
    Path should be a path to a directory not to a file.'''
    command = ['git', 'rev-parse', '--show-toplevel']
    path_to_toplevel = ''
    try:
        output = subprocess.check_output(  # nosec
            command, stderr=subprocess.DEVNULL, cwd=path)
        if isinstance(output, bytes):
            path_to_toplevel = output.decode('utf-8').split('\n').pop(0)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.debug("Cannot find git repo toplevel, path is %s", path)
    return path_to_toplevel