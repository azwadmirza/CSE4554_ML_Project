def _get_pip_bin(bin_env):
    '''
    Locate the pip binary, either from `bin_env` as a virtualenv, as the
    executable itself, or from searching conventional filesystem locations
    '''
    if not bin_env:
        which_result = __salt__['cmd.which_bin'](['pip', 'pip2', 'pip-python'])
        if which_result is None:
            raise CommandNotFoundError('Could not find a `pip` binary')
        if salt.utils.is_windows():
            return which_result.encode('string-escape')
        return which_result

    # try to get pip bin from virtualenv, bin_env
    if os.path.isdir(bin_env):
        if salt.utils.is_windows():
            pip_bin = os.path.join(
                bin_env, 'Scripts', 'pip.exe').encode('string-escape')
        else:
            pip_bin = os.path.join(bin_env, 'bin', 'pip')
        if os.path.isfile(pip_bin):
            return pip_bin
        msg = 'Could not find a `pip` binary in virtualenv {0}'.format(bin_env)
        raise CommandNotFoundError(msg)
    # bin_env is the pip binary
    elif os.access(bin_env, os.X_OK):
        if os.path.isfile(bin_env) or os.path.islink(bin_env):
            return bin_env
    else:
        raise CommandNotFoundError('Could not find a `pip` binary')