def managed(name, ppa=None, **kwargs):
    '''
    This state manages software package repositories. Currently, :mod:`yum
    <salt.modules.yumpkg>`, :mod:`apt <salt.modules.aptpkg>`, and :mod:`zypper
    <salt.modules.zypper>` repositories are supported.

    **YUM/DNF/ZYPPER-BASED SYSTEMS**

    .. note::
        One of ``baseurl`` or ``mirrorlist`` below is required. Additionally,
        note that this state is not presently capable of managing more than one
        repo in a single repo file, so each instance of this state will manage
        a single repo file containing the configuration for a single repo.

    name
        This value will be used in two ways: Firstly, it will be the repo ID,
        as seen in the entry in square brackets (e.g. ``[foo]``) for a given
        repo. Secondly, it will be the name of the file as stored in
        /etc/yum.repos.d (e.g. ``/etc/yum.repos.d/foo.conf``).

    enabled : True
        Whether or not the repo is enabled. Can be specified as True/False or
        1/0.

    disabled : False
        Included to reduce confusion due to APT's use of the ``disabled``
        argument. If this is passed for a YUM/DNF/Zypper-based distro, then the
        reverse will be passed as ``enabled``. For example passing
        ``disabled=True`` will assume ``enabled=False``.

    humanname
        This is used as the "name" value in the repo file in
        ``/etc/yum.repos.d/`` (or ``/etc/zypp/repos.d`` for SUSE distros).

    baseurl
        The URL to a yum repository

    mirrorlist
        A URL which points to a file containing a collection of baseurls

    comments
        Sometimes you want to supply additional information, but not as
        enabled configuration. Anything supplied for this list will be saved
        in the repo configuration with a comment marker (#) in front.

    gpgautoimport
        Only valid for Zypper package manager. If set to True, automatically
        trust and import public GPG key for the repository. The key should be
        specified with ``gpgkey`` parameter. See details below.

    Additional configuration values seen in YUM/DNF/Zypper repo files, such as
    ``gpgkey`` or ``gpgcheck``, will be used directly as key-value pairs.
    For example:

    .. code-block:: yaml

        foo:
          pkgrepo.managed:
            - humanname: Personal repo for foo
            - baseurl: https://mydomain.tld/repo/foo/$releasever/$basearch
            - gpgkey: file:///etc/pki/rpm-gpg/foo-signing-key
            - gpgcheck: 1


    **APT-BASED SYSTEMS**

    ppa
        On Ubuntu, you can take advantage of Personal Package Archives on
        Launchpad simply by specifying the user and archive name. The keyid
        will be queried from launchpad and everything else is set
        automatically. You can override any of the below settings by simply
        setting them as you would normally. For example:

        .. code-block:: yaml

            logstash-ppa:
              pkgrepo.managed:
                - ppa: wolfnet/logstash

    ppa_auth
        For Ubuntu PPAs there can be private PPAs that require authentication
        to access. For these PPAs the username/password can be passed as an
        HTTP Basic style username/password combination.

        .. code-block:: yaml

            logstash-ppa:
              pkgrepo.managed:
                - ppa: wolfnet/logstash
                - ppa_auth: username:password

    name
        On apt-based systems this must be the complete entry as it would be
        seen in the sources.list file.  This can have a limited subset of
        components (i.e. 'main') which can be added/modified with the
        ``comps`` option.

        .. code-block:: yaml

            precise-repo:
              pkgrepo.managed:
                - name: deb http://us.archive.ubuntu.com/ubuntu precise main

        .. note::

            The above example is intended as a more readable way of configuring
            the SLS, it is equivalent to the following:

            .. code-block:: yaml

                'deb http://us.archive.ubuntu.com/ubuntu precise main':
                  pkgrepo.managed

    disabled : False
        Toggles whether or not the repo is used for resolving dependencies
        and/or installing packages.

    enabled : True
        Included to reduce confusion due to YUM/DNF/Zypper's use of the
        ``enabled`` argument. If this is passed for an APT-based distro, then
        the reverse will be passed as ``disabled``. For example, passing
        ``enabled=False`` will assume ``disabled=False``.

    architectures
        On apt-based systems, architectures can restrict the available
        architectures that the repository provides (e.g. only amd64).
        architectures should be a comma-separated list.

    comps
        On apt-based systems, comps dictate the types of packages to be
        installed from the repository (e.g. main, nonfree, ...).  For
        purposes of this, comps should be a comma-separated list.

    file
       The filename for the .list that the repository is configured in.
       It is important to include the full-path AND make sure it is in
       a directory that APT will look in when handling packages

    dist
       This dictates the release of the distro the packages should be built
       for.  (e.g. unstable). This option is rarely needed.

    keyid
       The KeyID or a list of KeyIDs of the GPG key to install.
       This option also requires the ``keyserver`` option to be set.

    keyserver
       This is the name of the keyserver to retrieve gpg keys from.  The
       ``keyid`` option must also be set for this option to work.

    key_url
       URL to retrieve a GPG key from. Allows the usage of ``http://``,
       ``https://`` as well as ``salt://``.

       .. note::

           Use either ``keyid``/``keyserver`` or ``key_url``, but not both.

    key_text
        The string representation of the GPG key to install.

        .. versionadded:: 2018.3.0

       .. note::

           Use either ``keyid``/``keyserver``, ``key_url``, or ``key_text`` but
           not more than one method.

    consolidate : False
       If set to ``True``, this will consolidate all sources definitions to the
       sources.list file, cleanup the now unused files, consolidate components
       (e.g. main) for the same URI, type, and architecture to a single line,
       and finally remove comments from the sources.list file.  The consolidate
       will run every time the state is processed. The option only needs to be
       set on one repo managed by salt to take effect.

    clean_file : False
       If set to ``True``, empty the file before config repo

       .. note::
           Use with care. This can be dangerous if multiple sources are
           configured in the same file.

       .. versionadded:: 2015.8.0

    refresh : True
       If set to ``False`` this will skip refreshing the apt package database
       on debian based systems.

    refresh_db : True
       .. deprecated:: 2018.3.0
           Use ``refresh`` instead.

    require_in
       Set this to a list of pkg.installed or pkg.latest to trigger the
       running of apt-get update prior to attempting to install these
       packages. Setting a require in the pkg state will not work for this.
    '''
    if 'refresh_db' in kwargs:
        salt.utils.versions.warn_until(
            'Neon',
            'The \'refresh_db\' argument to \'pkg.mod_repo\' has been '
            'renamed to \'refresh\'. Support for using \'refresh_db\' will be '
            'removed in the Neon release of Salt.'
        )
        kwargs['refresh'] = kwargs.pop('refresh_db')

    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}

    if 'pkg.get_repo' not in __salt__:
        ret['result'] = False
        ret['comment'] = 'Repo management not implemented on this platform'
        return ret

    if 'key_url' in kwargs and ('keyid' in kwargs or 'keyserver' in kwargs):
        ret['result'] = False
        ret['comment'] = 'You may not use both "keyid"/"keyserver" and ' \
                         '"key_url" argument.'

    if 'key_text' in kwargs and ('keyid' in kwargs or 'keyserver' in kwargs):
        ret['result'] = False
        ret['comment'] = 'You may not use both "keyid"/"keyserver" and ' \
                         '"key_text" argument.'
    if 'key_text' in kwargs and ('key_url' in kwargs):
        ret['result'] = False
        ret['comment'] = 'You may not use both "key_url" and ' \
                         '"key_text" argument.'

    if 'repo' in kwargs:
        ret['result'] = False
        ret['comment'] = ('\'repo\' is not a supported argument for this '
                          'state. The \'name\' argument is probably what was '
                          'intended.')
        return ret

    enabled = kwargs.pop('enabled', None)
    disabled = kwargs.pop('disabled', None)

    if enabled is not None and disabled is not None:
        ret['result'] = False
        ret['comment'] = 'Only one of enabled/disabled is allowed'
        return ret
    elif enabled is None and disabled is None:
        # If neither argument was passed we assume the repo will be enabled
        enabled = True

    repo = name
    if __grains__['os'] in ('Ubuntu', 'Mint'):
        if ppa is not None:
            # overload the name/repo value for PPAs cleanly
            # this allows us to have one code-path for PPAs
            try:
                repo = ':'.join(('ppa', ppa))
            except TypeError:
                repo = ':'.join(('ppa', six.text_type(ppa)))

        kwargs['disabled'] = not salt.utils.data.is_true(enabled) \
            if enabled is not None \
            else salt.utils.data.is_true(disabled)

    elif __grains__['os_family'] in ('RedHat', 'Suse'):
        if 'humanname' in kwargs:
            kwargs['name'] = kwargs.pop('humanname')
        if 'name' not in kwargs:
            # Fall back to the repo name if humanname not provided
            kwargs['name'] = repo

        kwargs['enabled'] = not salt.utils.data.is_true(disabled) \
            if disabled is not None \
            else salt.utils.data.is_true(enabled)

    elif __grains__['os_family'] in ('NILinuxRT', 'Poky'):
        # opkg is the pkg virtual
        kwargs['enabled'] = not salt.utils.data.is_true(disabled) \
            if disabled is not None \
            else salt.utils.data.is_true(enabled)

    for kwarg in _STATE_INTERNAL_KEYWORDS:
        kwargs.pop(kwarg, None)

    try:
        pre = __salt__['pkg.get_repo'](repo=repo, **kwargs)
    except CommandExecutionError as exc:
        ret['result'] = False
        ret['comment'] = \
            'Failed to examine repo \'{0}\': {1}'.format(name, exc)
        return ret

    # This is because of how apt-sources works. This pushes distro logic
    # out of the state itself and into a module that it makes more sense
    # to use. Most package providers will simply return the data provided
    # it doesn't require any "specialized" data massaging.
    if 'pkg.expand_repo_def' in __salt__:
        sanitizedkwargs = __salt__['pkg.expand_repo_def'](repo=repo, **kwargs)
    else:
        sanitizedkwargs = kwargs

    if __grains__['os_family'] == 'Debian':
        repo = salt.utils.pkg.deb.strip_uri(repo)

    if pre:
        #22412: Remove file attribute in case same repo is set up multiple times but with different files
        pre.pop('file', None)
        sanitizedkwargs.pop('file', None)
        for kwarg in sanitizedkwargs:
            if kwarg not in pre:
                if kwarg == 'enabled':
                    # On a RedHat-based OS, 'enabled' is assumed to be true if
                    # not explicitly set, so we don't need to update the repo
                    # if it's desired to be enabled and the 'enabled' key is
                    # missing from the repo definition
                    if __grains__['os_family'] == 'RedHat':
                        if not salt.utils.data.is_true(sanitizedkwargs[kwarg]):
                            break
                    else:
                        break
                else:
                    break
            elif kwarg in ('comps', 'key_url'):
                if sorted(sanitizedkwargs[kwarg]) != sorted(pre[kwarg]):
                    break
            elif kwarg == 'line' and __grains__['os_family'] == 'Debian':
                # split the line and sort everything after the URL
                sanitizedsplit = sanitizedkwargs[kwarg].split()
                sanitizedsplit[3:] = sorted(sanitizedsplit[3:])
                reposplit, _, pre_comments = \
                    [x.strip() for x in pre[kwarg].partition('#')]
                reposplit = reposplit.split()
                reposplit[3:] = sorted(reposplit[3:])
                if sanitizedsplit != reposplit:
                    break
                if 'comments' in kwargs:
                    post_comments = \
                        salt.utils.pkg.deb.combine_comments(kwargs['comments'])
                    if pre_comments != post_comments:
                        break
            elif kwarg == 'comments' and __grains__['os_family'] == 'RedHat':
                precomments = salt.utils.pkg.rpm.combine_comments(pre[kwarg])
                kwargcomments = salt.utils.pkg.rpm.combine_comments(
                        sanitizedkwargs[kwarg])
                if precomments != kwargcomments:
                    break
            elif kwarg == 'architectures' and sanitizedkwargs[kwarg]:
                if set(sanitizedkwargs[kwarg]) != set(pre[kwarg]):
                    break
            else:
                if __grains__['os_family'] in ('RedHat', 'Suse') \
                        and any(isinstance(x, bool) for x in
                                (sanitizedkwargs[kwarg], pre[kwarg])):
                    # This check disambiguates 1/0 from True/False
                    if salt.utils.data.is_true(sanitizedkwargs[kwarg]) != \
                            salt.utils.data.is_true(pre[kwarg]):
                        break
                else:
                    if six.text_type(sanitizedkwargs[kwarg]) != six.text_type(pre[kwarg]):
                        break
        else:
            ret['result'] = True
            ret['comment'] = ('Package repo \'{0}\' already configured'
                              .format(name))
            return ret

    if __opts__['test']:
        ret['comment'] = (
            'Package repo \'{0}\' would be configured. This may cause pkg '
            'states to behave differently than stated if this action is '
            'repeated without test=True, due to the differences in the '
            'configured repositories.'.format(name)
        )
        if pre:
            for kwarg in sanitizedkwargs:
                if sanitizedkwargs.get(kwarg) != pre.get(kwarg):
                    ret['changes'][kwarg] = {'new': sanitizedkwargs.get(kwarg),
                                             'old': pre.get(kwarg)}
        else:
            ret['changes']['repo'] = name
        return ret

    # empty file before configure
    if kwargs.get('clean_file', False):
        with salt.utils.files.fopen(kwargs['file'], 'w'):
            pass

    try:
        if __grains__['os_family'] == 'Debian':
            __salt__['pkg.mod_repo'](repo, saltenv=__env__, **kwargs)
        else:
            __salt__['pkg.mod_repo'](repo, **kwargs)
    except Exception as exc:
        # This is another way to pass information back from the mod_repo
        # function.
        ret['result'] = False
        ret['comment'] = \
            'Failed to configure repo \'{0}\': {1}'.format(name, exc)
        return ret

    try:
        post = __salt__['pkg.get_repo'](repo=repo, **kwargs)
        if pre:
            for kwarg in sanitizedkwargs:
                if post.get(kwarg) != pre.get(kwarg):
                    ret['changes'][kwarg] = {'new': post.get(kwarg),
                                             'old': pre.get(kwarg)}
        else:
            ret['changes'] = {'repo': repo}

        ret['result'] = True
        ret['comment'] = 'Configured package repo \'{0}\''.format(name)
    except Exception as exc:
        ret['result'] = False
        ret['comment'] = \
            'Failed to confirm config of repo \'{0}\': {1}'.format(name, exc)

    # Clear cache of available packages, if present, since changes to the
    # repositories may change the packages that are available.
    if ret['changes']:
        sys.modules[
            __salt__['test.ping'].__module__
        ].__context__.pop('pkg._avail', None)

    return ret