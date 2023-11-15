def lsattr(path):
    '''
    .. versionadded:: 2018.3.0
    .. versionchanged:: 2018.3.1
        If ``lsattr`` is not installed on the system, ``None`` is returned.

    Obtain the modifiable attributes of the given file. If path
    is to a directory, an empty list is returned.

    path
        path to file to obtain attributes of. File/directory must exist.

    CLI Example:

    .. code-block:: bash

        salt '*' file.lsattr foo1.txt
    '''
    if not salt.utils.path.which('lsattr'):
        return None

    if not os.path.exists(path):
        raise SaltInvocationError("File or directory does not exist.")

    cmd = ['lsattr', path]
    result = __salt__['cmd.run'](cmd, ignore_retcode=True, python_shell=False)

    results = {}
    for line in result.splitlines():
        if not line.startswith('lsattr: '):
            vals = line.split(None, 1)
            results[vals[1]] = re.findall(r"[acdijstuADST]", vals[0])

    return results