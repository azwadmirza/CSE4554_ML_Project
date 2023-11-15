def __get_version(version, version_info):
    '''
    If we can get a version provided at installation time or from Git, use
    that instead, otherwise we carry on.
    '''
    try:
        # Try to import the version information provided at install time
        from salt._version import __version__, __version_info__  # pylint: disable=E0611
        return __version__, __version_info__
    except ImportError:
        pass

    # This might be a 'python setup.py develop' installation type. Let's
    # discover the version information at runtime.
    import os
    import warnings
    import subprocess

    try:
        cwd = os.path.abspath(os.path.dirname(__file__))
    except NameError:
        # We're most likely being frozen and __file__ triggered this NameError
        # Let's work around that
        import inspect
        cwd = os.path.abspath(
            os.path.dirname(inspect.getsourcefile(__get_version))
        )

    try:
        kwargs = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )

        if not sys.platform.startswith('win'):
            # Let's not import `salt.utils` for the above check
            kwargs['close_fds'] = True

        process = subprocess.Popen(
                ['git', 'describe', '--tags', '--match', 'v[0-9]*'], **kwargs)
        out, err = process.communicate()
        out = out.strip()
        err = err.strip()

        if not out or err:
            return version, version_info

        parsed_version = SaltStackVersion.parse(out)

        if parsed_version.info > version_info:
            warnings.warn(
                'The parsed version info, `{0}`, is bigger than the one '
                'defined in the file, `{1}`. Missing version bump?'.format(
                    parsed_version.info,
                    version_info
                ),
                UserWarning,
                stacklevel=2
            )
            return version, version_info
        elif parsed_version.info < version_info:
            warnings.warn(
                'The parsed version info, `{0}`, is lower than the one '
                'defined in the file, `{1}`.'
                'In order to get the proper salt version with the git hash '
                'you need to update salt\'s local git tags. Something like: '
                '\'git fetch --tags\' or \'git fetch --tags upstream\' if '
                'you followed salt\'s contribute documentation. The version '
                'string WILL NOT include the git hash.'.format(
                    parsed_version.info,
                    version_info
                ),
                UserWarning,
                stacklevel=2
            )
            return version, version_info
        return parsed_version.string, parsed_version.info
    except OSError as os_err:
        if os_err.errno != 2:
            # If the errno is not 2(The system cannot find the file
            # specified), raise the exception so it can be catch by the
            # developers
            raise
    return version, version_info