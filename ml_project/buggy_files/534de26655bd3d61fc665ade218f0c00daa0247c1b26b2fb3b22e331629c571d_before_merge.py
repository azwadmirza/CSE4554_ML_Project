def vcvars_command(settings, arch=None, compiler_version=None, force=False, vcvars_ver=None,
                   winsdk_version=None, output=None):
    output = default_output(output, 'conans.client.tools.win.vcvars_command')

    arch_setting = arch or settings.get_safe("arch")

    compiler = settings.get_safe("compiler")
    if compiler == 'Visual Studio':
        compiler_version = compiler_version or settings.get_safe("compiler.version")
    else:
        # vcvars might be still needed for other compilers, e.g. clang-cl or Intel C++,
        # as they might be using Microsoft STL and other tools
        # (e.g. resource compiler, manifest tool, etc)
        # in this case, use the latest Visual Studio available on the machine
        last_version = latest_vs_version_installed(output=output)

        compiler_version = compiler_version or last_version
    os_setting = settings.get_safe("os")
    if not compiler_version:
        raise ConanException("compiler.version setting required for vcvars not defined")

    # https://msdn.microsoft.com/en-us/library/f2ccy3wt.aspx
    arch_setting = arch_setting or 'x86_64'
    arch_build = settings.get_safe("arch_build") or detected_architecture()
    if os_setting == 'WindowsCE':
        vcvars_arch = "x86"
    elif arch_build == 'x86_64':
        # Only uses x64 tooling if arch_build explicitly defines it, otherwise
        # Keep the VS default, which is x86 toolset
        # This will probably be changed in conan 2.0
        if ((settings.get_safe("arch_build") or
                os.getenv("PreferredToolArchitecture") == "x64")
                and int(compiler_version) >= 12):
            x86_cross = "amd64_x86"
        else:
            x86_cross = "x86"
        vcvars_arch = {'x86': x86_cross,
                       'x86_64': 'amd64',
                       'armv7': 'amd64_arm',
                       'armv8': 'amd64_arm64'}.get(arch_setting)
    elif arch_build == 'x86':
        vcvars_arch = {'x86': 'x86',
                       'x86_64': 'x86_amd64',
                       'armv7': 'x86_arm',
                       'armv8': 'x86_arm64'}.get(arch_setting)

    if not vcvars_arch:
        raise ConanException('unsupported architecture %s' % arch_setting)

    existing_version = os.environ.get("VisualStudioVersion")

    if existing_version:
        command = ["echo Conan:vcvars already set"]
        existing_version = existing_version.split(".")[0]
        if existing_version != compiler_version:
            message = "Visual environment already set to %s\n " \
                      "Current settings visual version: %s" % (existing_version, compiler_version)
            if not force:
                raise ConanException("Error, %s" % message)
            else:
                output.warn(message)
    else:
        vs_path = vs_installation_path(str(compiler_version))

        if not vs_path or not os.path.isdir(vs_path):
            raise ConanException("VS non-existing installation: Visual Studio %s"
                                 % str(compiler_version))
        else:
            if int(compiler_version) > 14:
                vcvars_path = os.path.join(vs_path, "VC/Auxiliary/Build/vcvarsall.bat")
                command = ['set "VSCMD_START_DIR=%%CD%%" && '
                           'call "%s" %s' % (vcvars_path, vcvars_arch)]
            else:
                vcvars_path = os.path.join(vs_path, "VC/vcvarsall.bat")
                command = ['call "%s" %s' % (vcvars_path, vcvars_arch)]
        if int(compiler_version) >= 14:
            if winsdk_version:
                command.append(winsdk_version)
            if vcvars_ver:
                command.append("-vcvars_ver=%s" % vcvars_ver)

        if os_setting == 'WindowsStore':
            os_version_setting = settings.get_safe("os.version")
            if os_version_setting == '8.1':
                command.append('store 8.1')
            elif os_version_setting == '10.0':
                windows_10_sdk = find_windows_10_sdk()
                if not windows_10_sdk:
                    raise ConanException("cross-compiling for WindowsStore 10 (UWP), "
                                         "but Windows 10 SDK wasn't found")
                command.append('store %s' % windows_10_sdk)
            else:
                raise ConanException('unsupported Windows Store version %s' % os_version_setting)
    return " ".join(command)