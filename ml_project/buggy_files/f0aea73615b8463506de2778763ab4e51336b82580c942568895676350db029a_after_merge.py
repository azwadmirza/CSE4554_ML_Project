def _bootstrap_deb(
        root,
        arch,
        flavor,
        repo_url=None,
        static_qemu=None,
        pkgs=None,
        exclude_pkgs=None,
    ):
    '''
    Bootstrap an image using the Debian tools

    root
        The root of the image to install to. Will be created as a directory if
        if does not exist. (e.x.: /root/wheezy)

    arch
        Architecture of the target image. (e.x.: amd64)

    flavor
        Flavor of Debian to install. (e.x.: wheezy)

    repo_url
        Base URL for the mirror to install from.
        (e.x.: http://ftp.debian.org/debian/)

    static_qemu
        Local path to the static qemu binary required for this arch.
        (e.x.: /usr/bin/qemu-amd64-static)

    pkgs
        A list of packages to be installed on this image.

    exclude_pkgs
        A list of packages to be excluded.
    '''

    if repo_url is None:
        repo_url = 'http://ftp.debian.org/debian/'

    if not salt.utils.which('debootstrap'):
        log.error('Required tool debootstrap is not installed.')
        return False

    if static_qemu and not salt.utils.validate.path.is_executable(static_qemu):
        log.error('Required tool qemu not '
                  'present/readable at: {0}'.format(static_qemu))
        return False

    if isinstance(pkgs, (list, tuple)):
        pkgs = ','.join(pkgs)
    if isinstance(exclude_pkgs, (list, tuple)):
        exclude_pkgs = ','.join(exclude_pkgs)

    deb_args = [
        'debootstrap',
        '--foreign',
        '--arch',
        _cmd_quote(arch)]

    if pkgs:
        deb_args += ['--include', _cmd_quote(pkgs)]
    if exclude_pkgs:
        deb_args += ['--exclude', _cmd_quote(exclude_pkgs)]

    deb_args += [
        _cmd_quote(flavor),
        _cmd_quote(root),
        _cmd_quote(repo_url),
    ]

    __salt__['cmd.run'](deb_args, python_shell=False)

    if static_qemu:
        __salt__['cmd.run'](
            'cp {qemu} {root}/usr/bin/'.format(
                qemu=_cmd_quote(static_qemu), root=_cmd_quote(root)
            )
        )

    env = {'DEBIAN_FRONTEND': 'noninteractive',
           'DEBCONF_NONINTERACTIVE_SEEN': 'true',
           'LC_ALL': 'C',
           'LANGUAGE': 'C',
           'LANG': 'C',
           'PATH': '/sbin:/bin:/usr/bin'}
    __salt__['cmd.run'](
        'chroot {root} /debootstrap/debootstrap --second-stage'.format(
            root=_cmd_quote(root)
        ),
        env=env
    )
    __salt__['cmd.run'](
        'chroot {root} dpkg --configure -a'.format(
            root=_cmd_quote(root)
        ),
        env=env
    )