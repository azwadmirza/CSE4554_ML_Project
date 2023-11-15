def _find_chocolatey():
    '''
    Returns the full path to chocolatey.bat on the host.
    '''
    # Check context
    if 'chocolatey._path' in __context__:
        return __context__['chocolatey._path']

    # Check the path
    choc_path = __salt__['cmd.which']('chocolatey.exe')
    if choc_path:
        __context__['chocolatey._path'] = choc_path
        return __context__['chocolatey._path']

    # Check in common locations
    choc_defaults = [
        os.path.join(os.environ.get('ProgramData'), 'Chocolatey', 'bin', 'chocolatey.exe'),
        os.path.join(os.environ.get('SystemDrive'), 'Chocolatey', 'bin', 'chocolatey.bat')]
    for choc_exe in choc_defaults:
        if os.path.isfile(choc_exe):
            __context__['chocolatey._path'] = choc_exe
            return __context__['chocolatey._path']

    # Not installed, raise an error
    err = ('Chocolatey not installed. Use chocolatey.bootstrap to '
            'install the Chocolatey package manager.')
    raise CommandExecutionError(err)