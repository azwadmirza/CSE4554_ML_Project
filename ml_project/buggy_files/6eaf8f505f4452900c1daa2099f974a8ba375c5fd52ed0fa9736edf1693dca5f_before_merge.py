def get_info_dict(system=False):
    try:
        from ..install import linked_data
        root_pkgs = linked_data(context.root_prefix)
    except:  # pragma: no cover
        root_pkgs = {}

    try:
        from requests import __version__ as requests_version
        # These environment variables can influence requests' behavior, along with configuration
        # in a .netrc file
        #   REQUESTS_CA_BUNDLE
        #   HTTP_PROXY
        #   HTTPS_PROXY
    except ImportError:  # pragma: no cover
        try:
            from pip._vendor.requests import __version__ as requests_version
        except Exception as e:  # pragma: no cover
            requests_version = "Error %r" % e
    except Exception as e:  # pragma: no cover
        requests_version = "Error %r" % e

    try:
        from conda_env import __version__ as conda_env_version
    except:  # pragma: no cover
        try:
            cenv = [p for p in itervalues(root_pkgs) if p['name'] == 'conda-env']
            conda_env_version = cenv[0]['version']
        except:
            conda_env_version = "not installed"

    try:
        import conda_build
    except ImportError:  # pragma: no cover
        conda_build_version = "not installed"
    except Exception as e:  # pragma: no cover
        conda_build_version = "Error %s" % e
    else:  # pragma: no cover
        conda_build_version = conda_build.__version__

    channels = list(all_channel_urls(context.channels))
    if not context.json:
        channels = [c + ('' if offline_keep(c) else '  (offline)')
                    for c in channels]
    channels = [mask_anaconda_token(c) for c in channels]

    config_files = tuple(path for path in context.collect_all()
                         if path not in ('envvars', 'cmd_line'))

    netrc_file = os.environ.get('NETRC')
    if not netrc_file:
        user_netrc = expanduser("~/.netrc")
        if isfile(user_netrc):
            netrc_file = user_netrc

    active_prefix_name = env_name(context.active_prefix)

    info_dict = dict(
        platform=context.subdir,
        conda_version=conda_version,
        conda_env_version=conda_env_version,
        conda_build_version=conda_build_version,
        root_prefix=context.root_prefix,
        conda_prefix=context.conda_prefix,
        conda_private=conda_in_private_env(),
        root_writable=context.root_writable,
        pkgs_dirs=context.pkgs_dirs,
        envs_dirs=context.envs_dirs,
        default_prefix=context.default_prefix,
        active_prefix=context.active_prefix,
        active_prefix_name=active_prefix_name,
        conda_shlvl=context.shlvl,
        channels=channels,
        user_rc_path=user_rc_path,
        rc_path=user_rc_path,
        sys_rc_path=sys_rc_path,
        # is_foreign=bool(foreign),
        offline=context.offline,
        envs=[],
        python_version='.'.join(map(str, sys.version_info)),
        requests_version=requests_version,
        user_agent=context.user_agent,
        conda_location=CONDA_PACKAGE_ROOT,
        config_files=config_files,
        netrc_file=netrc_file,
    )
    if on_win:
        from ..common.platform import is_admin_on_windows
        info_dict['is_windows_admin'] = is_admin_on_windows()
    else:
        info_dict['UID'] = os.geteuid()
        info_dict['GID'] = os.getegid()

    if system:
        evars = {
            'CIO_TEST',
            'CONDA_DEFAULT_ENV',
            'CONDA_ENVS_PATH',
            'DYLD_LIBRARY_PATH',
            'FTP_PROXY',
            'HTTP_PROXY',
            'HTTPS_PROXY',
            'LD_LIBRARY_PATH',
            'PATH',
            'PYTHONHOME',
            'PYTHONPATH',
            'REQUESTS_CA_BUNDLE',
            'SSL_CERT_FILE',
        }

        evars.update(v for v in os.environ if v.startswith('CONDA_'))
        evars.update(v for v in os.environ if v.startswith('conda_'))

        info_dict.update({
            'sys.version': sys.version,
            'sys.prefix': sys.prefix,
            'sys.executable': sys.executable,
            'site_dirs': get_user_site(),
            'env_vars': {ev: os.getenv(ev, os.getenv(ev.lower(), '<not set>')) for ev in evars},
        })

    return info_dict