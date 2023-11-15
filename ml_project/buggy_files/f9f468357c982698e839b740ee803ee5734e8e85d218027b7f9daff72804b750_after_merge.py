def _check_valid_version(salt):
    '''
    Check the version of npm to ensure this module will work. Currently
    npm must be at least version 1.2.
    '''
    # pylint: disable=no-member
    npm_version = distutils.version.LooseVersion(
        salt['cmd.run']('npm --version'))
    valid_version = distutils.version.LooseVersion('1.2')
    # pylint: enable=no-member
    if npm_version < valid_version:
        raise CommandExecutionError(
            '\'npm\' is not recent enough({0} < {1}). Please Upgrade.'.format(
                npm_version, valid_version
            )
        )