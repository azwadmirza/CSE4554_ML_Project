def install(gems,           # pylint: disable=C0103
            ruby=None,
            gem_bin=None,
            runas=None,
            version=None,
            rdoc=False,
            ri=False,
            pre_releases=False,
            proxy=None,
            source=None):      # pylint: disable=C0103
    '''
    Installs one or several gems.

    :param gems: string
        The gems to install
    :param gem_bin: string : None
        Full path to ``gem`` binary to use.
    :param ruby: string : None
        If RVM or rbenv are installed, the ruby version and gemset to use.
        Ignored if ``gem_bin`` is specified.
    :param runas: string : None
        The user to run gem as.
    :param version: string : None
        Specify the version to install for the gem.
        Doesn't play nice with multiple gems at once
    :param rdoc: boolean : False
        Generate RDoc documentation for the gem(s).
    :param ri: boolean : False
        Generate RI documentation for the gem(s).
    :param pre_releases: boolean : False
        Include pre-releases in the available versions
    :param proxy: string : None
        Use the specified HTTP proxy server for all outgoing traffic.
        Format: http://hostname[:port]

    source : None
        Use the specified HTTP gem source server to download gem.
        Format: http://hostname[:port]

    CLI Example:

    .. code-block:: bash

        salt '*' gem.install vagrant

        salt '*' gem.install redphone gem_bin=/opt/sensu/embedded/bin/gem
    '''
    try:
        gems = gems.split()
    except AttributeError:
        pass

    options = []
    if version:
        options.extend(['--version', version])
    if not rdoc:
        options.append('--no-rdoc')
    if not ri:
        options.append('--no-ri')
    if pre_releases:
        options.append('--pre')
    if proxy:
        options.extend(['-p', proxy])
    if source:
        options.extend(['--source', source])

    return _gem(['install'] + gems + options,
                ruby,
                gem_bin=gem_bin,
                runas=runas)