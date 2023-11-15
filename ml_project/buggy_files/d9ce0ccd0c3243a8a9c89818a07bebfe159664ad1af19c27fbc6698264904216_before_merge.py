def _check_pkg_version_format(pkg):
    '''
    Takes a package name and version specification (if any) and checks it using
    the pip library.
    '''

    ret = {'result': False, 'comment': None,
           'prefix': None, 'version_spec': None}

    if not HAS_PIP:
        ret['comment'] = (
            'An importable pip module is required but could not be found on '
            'your system. This usually means that the system''s pip package '
            'is not installed properly.'
        )

        return ret

    from_vcs = False
    try:
        # Get the requirement object from the pip library
        try:
            # With pip < 1.2, the __version__ attribute does not exist and
            # vcs+URL urls are not properly parsed.
            # The next line is meant to trigger an AttributeError and
            # handle lower pip versions
            logger.debug(
                'Installed pip version: {0}'.format(pip.__version__)
            )
            install_req = pip.req.InstallRequirement.from_line(pkg)
        except AttributeError:
            logger.debug('Installed pip version is lower than 1.2')
            supported_vcs = ('git', 'svn', 'hg', 'bzr')
            if pkg.startswith(supported_vcs):
                for vcs in supported_vcs:
                    if pkg.startswith(vcs):
                        from_vcs = True
                        install_req = pip.req.InstallRequirement.from_line(
                            pkg.split('{0}+'.format(vcs))[-1]
                        )
                        break
            else:
                install_req = pip.req.InstallRequirement.from_line(pkg)
    except (ValueError, InstallationError) as exc:
        ret['result'] = False
        if not from_vcs and '=' in pkg and '==' not in pkg:
            ret['comment'] = (
                'Invalid version specification in package {0}. \'=\' is '
                'not supported, use \'==\' instead.'.format(pkg)
            )
            return ret
        ret['comment'] = (
            'pip raised an exception while parsing {0!r}: {1}'.format(
                pkg, exc
            )
        )
        return ret

    if install_req.req is None:
        # This is most likely an url and there's no way to know what will
        # be installed before actually installing it.
        ret['result'] = True
        ret['prefix'] = ''
        ret['version_spec'] = []
    else:
        ret['result'] = True
        ret['prefix'] = re.sub('[^A-Za-z0-9.]+', '-', install_req.name)
        if hasattr(install_req, "specifier"):
            specifier = install_req.specifier
        else:
            specifier = install_req.req.specifier
        ret['version_spec'] = [(spec.operator, spec.version) for spec in specifier]

    return ret