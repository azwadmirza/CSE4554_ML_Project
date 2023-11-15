def _find_chocolatey(context, salt):
    '''
    Returns the full path to chocolatey.bat on the host.
    '''
    if 'chocolatey._path' in context:
        return context['chocolatey._path']
    choc_defaults = ['C:\\Chocolatey\\bin\\chocolatey.bat',
                     'C:\\ProgramData\\Chocolatey\\bin\\chocolatey.exe', ]

    choc_path = salt['cmd.which']('chocolatey.exe')
    if not choc_path:
        for choc_dir in choc_defaults:
            if salt['cmd.has_exec'](choc_dir):
                choc_path = choc_dir
    if not choc_path:
        err = ('Chocolatey not installed. Use chocolatey.bootstrap to '
                'install the Chocolatey package manager.')
        raise CommandExecutionError(err)
    context['chocolatey._path'] = choc_path
    return choc_path