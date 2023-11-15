def bootstrap(force=False):
    '''
    Download and install the latest version of the Chocolatey package manager
    via the official bootstrap.

    Chocolatey requires Windows PowerShell and the .NET v4.0 runtime. Depending
    on the host's version of Windows, chocolatey.bootstrap will attempt to
    ensure these prerequisites are met by downloading and executing the
    appropriate installers from Microsoft.

    Note that if PowerShell is installed, you may have to restart the host
    machine for Chocolatey to work.

    force
        Run the bootstrap process even if Chocolatey is found in the path.

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.bootstrap
        salt '*' chocolatey.bootstrap force=True
    '''
    # Check if Chocolatey is already present in the path
    try:
        choc_path = _find_chocolatey()
    except CommandExecutionError:
        choc_path = None
    if choc_path and not force:
        return 'Chocolatey found at {0}'.format(choc_path)

    # The following lookup tables are required to determine the correct
    # download required to install PowerShell. That's right, there's more
    # than one! You're welcome.
    ps_downloads = {
        ('Vista', 'x86'): 'http://download.microsoft.com/download/A/7/5/A75BC017-63CE-47D6-8FA4-AFB5C21BAC54/Windows6.0-KB968930-x86.msu',
        ('Vista', 'AMD64'): 'http://download.microsoft.com/download/3/C/8/3C8CF51E-1D9D-4DAA-AAEA-5C48D1CD055C/Windows6.0-KB968930-x64.msu',
        ('2008Server', 'x86'): 'http://download.microsoft.com/download/F/9/E/F9EF6ACB-2BA8-4845-9C10-85FC4A69B207/Windows6.0-KB968930-x86.msu',
        ('2008Server', 'AMD64'): 'http://download.microsoft.com/download/2/8/6/28686477-3242-4E96-9009-30B16BED89AF/Windows6.0-KB968930-x64.msu'
    }

    # It took until .NET v4.0 for Microsoft got the hang of making installers,
    # this should work under any version of Windows
    net4_url = 'http://download.microsoft.com/download/1/B/E/1BE39E79-7E39-46A3-96FF-047F95396215/dotNetFx40_Full_setup.exe'

    temp_dir = tempfile.gettempdir()

    # Check if PowerShell is installed. This should be the case for every
    # Windows release following Server 2008.
    ps_path = 'C:\\Windows\\SYSTEM32\\WindowsPowerShell\\v1.0\\powershell.exe'

    if not __salt__['cmd.has_exec'](ps_path):
        if (__grains__['osrelease'], __grains__['cpuarch']) in ps_downloads:
            # Install the appropriate release of PowerShell v2.0
            url = ps_downloads[(__grains__['osrelease'], __grains__['cpuarch'])]
            dest = os.path.join(temp_dir, 'powershell.exe')
            __salt__['cp.get_url'](url, dest)
            cmd = [dest, '/quiet', '/norestart']
            result = __salt__['cmd.run_all'](cmd, python_shell=False)
            if result['retcode'] != 0:
                err = ('Installing Windows PowerShell failed. Please run the '
                       'installer GUI on the host to get a more specific '
                       'reason.')
                raise CommandExecutionError(err)
        else:
            err = 'Windows PowerShell not found'
            raise CommandNotFoundError(err)

    # Run the .NET Framework 4 web installer
    dest = os.path.join(temp_dir, 'dotnet4.exe')
    __salt__['cp.get_url'](net4_url, dest)
    cmd = [dest, '/q', '/norestart']
    result = __salt__['cmd.run_all'](cmd, python_shell=False)
    if result['retcode'] != 0:
        err = ('Installing .NET v4.0 failed. Please run the installer GUI on '
               'the host to get a more specific reason.')
        raise CommandExecutionError(err)

    # Run the Chocolatey bootstrap.
    cmd = (
        '{0} -NoProfile -ExecutionPolicy unrestricted '
        '-Command "iex ((new-object net.webclient).'
        'DownloadString(\'https://chocolatey.org/install.ps1\'))" '
        '&& SET PATH=%PATH%;%systemdrive%\\chocolatey\\bin'
        .format(ps_path)
    )
    result = __salt__['cmd.run_all'](cmd, python_shell=True)

    if result['retcode'] != 0:
        err = 'Bootstrapping Chocolatey failed: {0}'.format(result['stderr'])
        raise CommandExecutionError(err)

    return result['stdout']