def execute(args, parser):
    import os
    from os.path import dirname

    import conda
    from conda.base.context import context
    from conda.models.channel import offline_keep
    from conda.resolve import Resolve
    from conda.api import get_index
    from conda.connection import user_agent

    if args.root:
        if context.json:
            stdout_json({'root_prefix': context.root_prefix})
        else:
            print(context.root_prefix)
        return

    if args.packages:
        index = get_index()
        r = Resolve(index)
        if context.json:
            stdout_json({
                package: [dump_record(r.index[d])
                          for d in r.get_dists_for_spec(arg2spec(package))]
                for package in args.packages
            })
        else:
            for package in args.packages:
                for dist in r.get_dists_for_spec(arg2spec(package)):
                    pretty_package(dist, r.index[dist])
        return

    options = 'envs', 'system', 'license'

    try:
        from conda.install import linked_data
        root_pkgs = linked_data(context.root_prefix)
    except:
        root_pkgs = None

    try:
        import requests
        requests_version = requests.__version__
    except ImportError:
        requests_version = "could not import"
    except Exception as e:
        requests_version = "Error %s" % e

    try:
        import conda_env
        conda_env_version = conda_env.__version__
    except:
        try:
            cenv = [p for p in itervalues(root_pkgs) if p['name'] == 'conda-env']
            conda_env_version = cenv[0]['version']
        except:
            conda_env_version = "not installed"

    try:
        import conda_build
    except ImportError:
        conda_build_version = "not installed"
    except Exception as e:
        conda_build_version = "Error %s" % e
    else:
        conda_build_version = conda_build.__version__

    channels = context.channels

    if args.unsafe_channels:
        if not context.json:
            print("\n".join(channels))
        else:
            print(json.dumps({"channels": channels}))
        return 0

    channels = list(prioritize_channels(channels).keys())
    if not context.json:
        channels = [c + ('' if offline_keep(c) else '  (offline)')
                    for c in channels]
    channels = [mask_anaconda_token(c) for c in channels]

    info_dict = dict(
        platform=context.subdir,
        conda_version=conda.__version__,
        conda_env_version=conda_env_version,
        conda_build_version=conda_build_version,
        root_prefix=context.root_prefix,
        conda_prefix=context.conda_prefix,
        conda_private=context.conda_private,
        root_writable=context.root_writable,
        pkgs_dirs=context.pkgs_dirs,
        envs_dirs=context.envs_dirs,
        default_prefix=context.default_prefix,
        channels=channels,
        rc_path=rc_path,
        user_rc_path=user_rc_path,
        sys_rc_path=sys_rc_path,
        # is_foreign=bool(foreign),
        offline=context.offline,
        envs=[],
        python_version='.'.join(map(str, sys.version_info)),
        requests_version=requests_version,
        user_agent=user_agent,
    )
    if not on_win:
        info_dict['UID'] = os.geteuid()
        info_dict['GID'] = os.getegid()

    if args.all or context.json:
        for option in options:
            setattr(args, option, True)

    if (args.all or all(not getattr(args, opt) for opt in options)) and not context.json:
        for key in 'pkgs_dirs', 'envs_dirs', 'channels':
            info_dict['_' + key] = ('\n' + 26 * ' ').join(info_dict[key])
        info_dict['_rtwro'] = ('writable' if info_dict['root_writable'] else
                               'read only')
        print("""\
Current conda install:

               platform : %(platform)s
          conda version : %(conda_version)s
       conda is private : %(conda_private)s
      conda-env version : %(conda_env_version)s
    conda-build version : %(conda_build_version)s
         python version : %(python_version)s
       requests version : %(requests_version)s
       root environment : %(root_prefix)s  (%(_rtwro)s)
    default environment : %(default_prefix)s
       envs directories : %(_envs_dirs)s
          package cache : %(_pkgs_dirs)s
           channel URLs : %(_channels)s
            config file : %(rc_path)s
           offline mode : %(offline)s
             user-agent : %(user_agent)s\
""" % info_dict)

        if not on_win:
            print("""\
                UID:GID : %(UID)s:%(GID)s
""" % info_dict)
        else:
            print()

    if args.envs:
        handle_envs_list(info_dict['envs'], not context.json)

    if args.system:
        from conda.cli.find_commands import find_commands, find_executable

        site_dirs = get_user_site()
        evars = ['PATH', 'PYTHONPATH', 'PYTHONHOME', 'CONDA_DEFAULT_ENV',
                 'CIO_TEST', 'CONDA_ENVS_PATH']

        if context.platform == 'linux':
            evars.append('LD_LIBRARY_PATH')
        elif context.platform == 'osx':
            evars.append('DYLD_LIBRARY_PATH')

        if context.json:
            info_dict['sys.version'] = sys.version
            info_dict['sys.prefix'] = sys.prefix
            info_dict['sys.executable'] = sys.executable
            info_dict['site_dirs'] = get_user_site()
            info_dict['env_vars'] = {ev: os.getenv(ev, '<not set>') for ev in evars}
        else:
            print("sys.version: %s..." % (sys.version[:40]))
            print("sys.prefix: %s" % sys.prefix)
            print("sys.executable: %s" % sys.executable)
            print("conda location: %s" % dirname(conda.__file__))
            for cmd in sorted(set(find_commands() + ['build'])):
                print("conda-%s: %s" % (cmd, find_executable('conda-' + cmd)))
            print("user site dirs: ", end='')
            if site_dirs:
                print(site_dirs[0])
            else:
                print()
            for site_dir in site_dirs[1:]:
                print('                %s' % site_dir)
            print()

            for ev in sorted(evars):
                print("%s: %s" % (ev, os.getenv(ev, '<not set>')))
            print()

    if args.license and not context.json:
        try:
            from _license import show_info
            show_info()
        except ImportError:
            print("""\
WARNING: could not import _license.show_info
# try:
# $ conda install -n root _license""")

    if context.json:
        stdout_json(info_dict)