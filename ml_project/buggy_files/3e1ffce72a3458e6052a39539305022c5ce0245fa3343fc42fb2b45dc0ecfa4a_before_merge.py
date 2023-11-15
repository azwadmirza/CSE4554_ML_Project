def _install_requirements(session, transport, *extra_requirements):
    # Install requirements
    distro_requirements = None

    pydir = _get_pydir(session)

    if IS_WINDOWS:
        _distro_requirements = os.path.join(REPO_ROOT,
                                            'requirements',
                                            'static',
                                            pydir,
                                            '{}-windows.txt'.format(transport))
        if os.path.exists(_distro_requirements):
            distro_requirements = _distro_requirements
        if distro_requirements:
            with open(distro_requirements) as rfh:
                for line in rfh.read().strip().splitlines():
                    # There are some SSL issues with distutils when installing pylxd which
                    # tries to install pbr, so lets just install pbr first
                    if line.startswith('pbr='):
                        session.install(
                            '--progress-bar=off',
                            line.split()[0].strip(),
                            silent=PIP_INSTALL_SILENT)
    else:
        _install_system_packages(session)
        distro = _get_distro_info(session)
        distro_keys = [
            '{id}'.format(**distro),
            '{id}-{version}'.format(**distro),
            '{id}-{version_parts[major]}'.format(**distro)
        ]
        for distro_key in distro_keys:
            _distro_requirements = os.path.join(REPO_ROOT,
                                                'requirements',
                                                'static',
                                                pydir,
                                                '{}-{}.txt'.format(transport, distro_key))
            if os.path.exists(_distro_requirements):
                distro_requirements = _distro_requirements
                break

    if distro_requirements is not None:
        _requirements_files = [distro_requirements]
        requirements_files = []
    else:
        _requirements_files = [
            os.path.join(REPO_ROOT, 'requirements', 'pytest.txt')
        ]
        if sys.platform.startswith('linux'):
            requirements_files = [
                os.path.join(REPO_ROOT, 'requirements', 'tests.txt')
            ]
        elif sys.platform.startswith('win'):
            requirements_files = [
                os.path.join(REPO_ROOT, 'pkg', 'windows', 'req.txt'),
            ]
        elif sys.platform.startswith('darwin'):
            requirements_files = [
                os.path.join(REPO_ROOT, 'pkg', 'osx', 'req.txt'),
                os.path.join(REPO_ROOT, 'pkg', 'osx', 'req_ext.txt'),
            ]

    while True:
        if not requirements_files:
            break
        requirements_file = requirements_files.pop(0)

        if requirements_file not in _requirements_files:
            _requirements_files.append(requirements_file)

        session.log('Processing {}'.format(requirements_file))
        with open(requirements_file) as rfh:  # pylint: disable=resource-leakage
            for line in rfh:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('-r'):
                    reqfile = os.path.join(os.path.dirname(requirements_file), line.strip().split()[-1])
                    if reqfile in _requirements_files:
                        continue
                    _requirements_files.append(reqfile)
                    continue

    for requirements_file in _requirements_files:
        session.install('--progress-bar=off', '-r', requirements_file, silent=PIP_INSTALL_SILENT)

    if extra_requirements:
        session.install('--progress-bar=off', *extra_requirements, silent=PIP_INSTALL_SILENT)