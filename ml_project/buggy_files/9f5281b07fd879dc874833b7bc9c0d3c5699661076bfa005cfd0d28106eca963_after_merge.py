def distutils_scheme(dist_name, user=False, home=None, root=None,
                     isolated=False, prefix=None):
    # type:(str, bool, str, str, bool, str) -> dict
    """
    Return a distutils install scheme
    """
    from distutils.dist import Distribution

    scheme = {}

    if isolated:
        extra_dist_args = {"script_args": ["--no-user-cfg"]}
    else:
        extra_dist_args = {}
    dist_args = {'name': dist_name}  # type: Dict[str, Union[str, List[str]]]
    dist_args.update(extra_dist_args)

    d = Distribution(dist_args)
    # Ignoring, typeshed issue reported python/typeshed/issues/2567
    d.parse_config_files()
    # NOTE: Ignoring type since mypy can't find attributes on 'Command'
    i = d.get_command_obj('install', create=True)  # type: Any
    assert i is not None
    # NOTE: setting user or home has the side-effect of creating the home dir
    # or user base for installations during finalize_options()
    # ideally, we'd prefer a scheme class that has no side-effects.
    assert not (user and prefix), "user={} prefix={}".format(user, prefix)
    assert not (home and prefix), "home={} prefix={}".format(home, prefix)
    i.user = user or i.user
    if user or home:
        i.prefix = ""
    i.prefix = prefix or i.prefix
    i.home = home or i.home
    i.root = root or i.root
    i.finalize_options()
    for key in SCHEME_KEYS:
        scheme[key] = getattr(i, 'install_' + key)

    # install_lib specified in setup.cfg should install *everything*
    # into there (i.e. it takes precedence over both purelib and
    # platlib).  Note, i.install_lib is *always* set after
    # finalize_options(); we only want to override here if the user
    # has explicitly requested it hence going back to the config

    # Ignoring, typeshed issue reported python/typeshed/issues/2567
    if 'install_lib' in d.get_option_dict('install'):  # type: ignore
        scheme.update(dict(purelib=i.install_lib, platlib=i.install_lib))

    if running_under_virtualenv():
        scheme['headers'] = os.path.join(
            sys.prefix,
            'include',
            'site',
            'python' + sys.version[:3],
            dist_name,
        )

        if root is not None:
            path_no_drive = os.path.splitdrive(
                os.path.abspath(scheme["headers"]))[1]
            scheme["headers"] = os.path.join(
                root,
                path_no_drive[1:],
            )

    return scheme