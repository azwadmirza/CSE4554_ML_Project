def purged(name,
           version=None,
           pkgs=None,
           normalize=True,
           ignore_epoch=False,
           **kwargs):
    '''
    Verify that a package is not installed, calling ``pkg.purge`` if necessary
    to purge the package. All configuration files are also removed.

    name
        The name of the package to be purged.

    version
        The version of the package that should be removed. Don't do anything if
        the package is installed with an unmatching version.

        .. important::
            As of version 2015.8.7, for distros which use yum/dnf, packages
            which have a version with a nonzero epoch (that is, versions which
            start with a number followed by a colon like in the example above)
            must have the epoch included when specifying the version number.
            For example:

            .. code-block:: yaml

                vim-enhanced:
                  pkg.installed:
                    - version: 2:7.4.160-1.el7

            In version 2015.8.9, an **ignore_epoch** argument has been added to
            :py:mod:`pkg.installed <salt.states.pkg.installed>`,
            :py:mod:`pkg.removed <salt.states.pkg.installed>`, and
            :py:mod:`pkg.purged <salt.states.pkg.installed>` states, which
            causes the epoch to be disregarded when the state checks to see if
            the desired version was installed. If **ignore_epoch** was not set
            to ``True``, and instead of ``2:7.4.160-1.el7`` a version of
            ``7.4.160-1.el7`` were used, this state would report success since
            the actual installed version includes the epoch, and the specified
            version would not match.

    normalize : True
        Normalize the package name by removing the architecture, if the
        architecture of the package is different from the architecture of the
        operating system. The ability to disable this behavior is useful for
        poorly-created packages which include the architecture as an actual
        part of the name, such as kernel modules which match a specific kernel
        version.

        .. versionadded:: 2015.8.0

    ignore_epoch : False
        When a package version contains an non-zero epoch (e.g.
        ``1:3.14.159-2.el7``, and a specific version of a package is desired,
        set this option to ``True`` to ignore the epoch when comparing
        versions. This allows for the following SLS to be used:

        .. code-block:: yaml

            # Actual vim-enhanced version: 2:7.4.160-1.el7
            vim-enhanced:
              pkg.purged:
                - version: 7.4.160-1.el7
                - ignore_epoch: True

        Without this option set to ``True`` in the above example, the state
        would falsely report success since the actual installed version is
        ``2:7.4.160-1.el7``. Alternatively, this option can be left as
        ``False`` and the full version string (with epoch) can be specified in
        the SLS file:

        .. code-block:: yaml

            vim-enhanced:
              pkg.purged:
                - version: 2:7.4.160-1.el7

        .. versionadded:: 2015.8.9

    Multiple Package Options:

    pkgs
        A list of packages to purge. Must be passed as a python list. The
        ``name`` parameter will be ignored if this option is passed. It accepts
        version numbers as well.

    .. versionadded:: 0.16.0
    '''
    try:
        return _uninstall(action='purge', name=name, version=version,
                          pkgs=pkgs, normalize=normalize,
                          ignore_epoch=ignore_epoch, **kwargs)
    except CommandExecutionError as exc:
        ret = {'name': name, 'result': False}
        if exc.info:
            # Get information for state return from the exception.
            ret['changes'] = exc.info.get('changes', {})
            ret['comment'] = exc.strerror_without_changes
        else:
            ret['changes'] = {}
            ret['comment'] = ('An error was encountered while purging '
                              'package(s): {0}'.format(exc))
        return ret