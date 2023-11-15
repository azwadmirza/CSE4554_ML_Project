def autodetect_vs_version(build):
    vs_version = os.getenv('VisualStudioVersion', None)
    vs_install_dir = os.getenv('VSINSTALLDIR', None)
    if not vs_version and not vs_install_dir:
        raise MesonException('Could not detect Visual Studio: VisualStudioVersion and VSINSTALLDIR are unset!\n'
                             'Are we inside a Visual Studio build environment? '
                             'You can also try specifying the exact backend to use.')
    # VisualStudioVersion is set since Visual Studio 12.0, but sometimes
    # vcvarsall.bat doesn't set it, so also use VSINSTALLDIR
    if vs_version == '14.0' or 'Visual Studio 14' in vs_install_dir:
        from mesonbuild.backend.vs2015backend import Vs2015Backend
        return Vs2015Backend(build)
    if vs_version == '15.0' or 'Visual Studio 17' in vs_install_dir or \
       'Visual Studio\\2017' in vs_install_dir:
        from mesonbuild.backend.vs2017backend import Vs2017Backend
        return Vs2017Backend(build)
    if 'Visual Studio 10.0' in vs_install_dir:
        return Vs2010Backend(build)
    raise MesonException('Could not detect Visual Studio using VisualStudioVersion: {!r} or VSINSTALLDIR: {!r}!\n'
                         'Please specify the exact backend to use.'.format(vs_version, vs_install_dir))