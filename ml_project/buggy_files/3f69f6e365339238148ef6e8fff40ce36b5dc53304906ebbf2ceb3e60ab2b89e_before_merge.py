def group_installed(name, skip=None, include=None, **kwargs):
    '''
    .. versionadded:: 2015.8.0

    Ensure that an entire package group is installed. This state is currently
    only supported for the :mod:`yum <salt.modules.yumpkg>` package manager.

    skip
        Packages that would normally be installed by the package group
        ("default" packages), which should not be installed.

        .. code-block:: yaml

            Load Balancer:
              pkg.group_installed:
                - skip:
                  - piranha

    include
        Packages which are included in a group, which would not normally be
        installed by a ``yum groupinstall`` ("optional" packages). Note that
        this will not enforce group membership; if you include packages which
        are not members of the specified groups, they will still be installed.

        .. code-block:: yaml

            Load Balancer:
              pkg.group_installed:
                - include:
                  - haproxy

        .. versionchanged:: 2016.3.0
            This option can no longer be passed as a comma-separated list, it
            must now be passed as a list (as shown in the above example).

    .. note::
        Because this is essentially a wrapper around :py:func:`pkg.install
        <salt.modules.yumpkg.install>`, any argument which can be passed to
        pkg.install may also be included here, and it will be passed on to the
        call to :py:func:`pkg.install <salt.modules.yumpkg.install>`.
    '''
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if 'pkg.group_diff' not in __salt__:
        ret['comment'] = 'pkg.group_install not available for this platform'
        return ret

    if skip is None:
        skip = []
    else:
        if not isinstance(skip, list):
            ret['comment'] = 'skip must be formatted as a list'
            return ret
        for idx, item in enumerate(skip):
            if not isinstance(item, six.string_types):
                skip[idx] = str(item)

    if include is None:
        include = []
    else:
        if not isinstance(include, list):
            ret['comment'] = 'include must be formatted as a list'
            return ret
        for idx, item in enumerate(include):
            if not isinstance(item, six.string_types):
                include[idx] = str(item)

    diff = __salt__['pkg.group_diff'](name)
    mandatory = diff['mandatory']['installed'] + \
        diff['mandatory']['not installed']

    invalid_skip = [x for x in mandatory if x in skip]
    if invalid_skip:
        ret['comment'] = (
            'The following mandatory packages cannot be skipped: {0}'
            .format(', '.join(invalid_skip))
        )
        return ret

    targets = diff['mandatory']['not installed']
    targets.extend([x for x in diff['default']['not installed']
                    if x not in skip])
    targets.extend(include)

    if not targets:
        ret['result'] = True
        ret['comment'] = 'Group \'{0}\' is already installed'.format(name)
        return ret

    partially_installed = diff['mandatory']['installed'] \
        or diff['default']['installed'] \
        or diff['optional']['installed']

    if __opts__['test']:
        ret['result'] = None
        if partially_installed:
            ret['comment'] = (
                'Group \'{0}\' is partially installed and will be updated'
                .format(name)
            )
        else:
            ret['comment'] = 'Group \'{0}\' will be installed'.format(name)
        return ret

    try:
        ret['changes'] = __salt__['pkg.install'](pkgs=targets, **kwargs)
    except CommandExecutionError as exc:
        ret = {'name': name, 'result': False}
        if exc.info:
            # Get information for state return from the exception.
            ret['changes'] = exc.info.get('changes', {})
            ret['comment'] = exc.strerror_without_changes
        else:
            ret['changes'] = {}
            ret['comment'] = ('An error was encountered while '
                              'installing/updating group \'{0}\': {1}'
                              .format(name, exc))
        return ret

    failed = [x for x in targets if x not in __salt__['pkg.list_pkgs']()]
    if failed:
        ret['comment'] = (
            'Failed to install the following packages: {0}'
            .format(', '.join(failed))
        )
        return ret

    ret['result'] = True
    ret['comment'] = 'Group \'{0}\' was {1}'.format(
        name,
        'updated' if partially_installed else 'installed'
    )
    return ret