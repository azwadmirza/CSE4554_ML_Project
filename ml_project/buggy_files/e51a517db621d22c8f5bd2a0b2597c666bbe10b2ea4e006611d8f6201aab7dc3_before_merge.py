def execute(args, parser):
    import os
    from os.path import dirname

    import conda
    from conda.config import (root_dir, get_channel_urls, subdir, pkgs_dirs,
                              root_writable, envs_dirs, default_prefix, rc_path,
                              user_rc_path, sys_rc_path, foreign, hide_binstar_tokens,
                              platform)
    from conda.resolve import Resolve
    from conda.cli.main_init import is_initialized
    from conda.api import get_index

    if args.root:
        if args.json:
            common.stdout_json({'root_prefix': root_dir})
        else:
            print(root_dir)
        return

    if args.packages:
        index = get_index()
        r = Resolve(index)
        if args.json:
            common.stdout_json({
                package: [p._asdict()
                          for p in sorted(r.get_pkgs(common.arg2spec(package)))]
                for package in args.packages
            })
        else:
            for package in args.packages:
                versions = r.get_pkgs(common.arg2spec(package))
                for pkg in sorted(versions):
                    pretty_package(pkg)
        return

    options = 'envs', 'system', 'license'

    try:
        import requests
        requests_version = requests.__version__
    except ImportError:
        requests_version = "could not import"
    except Exception as e:
        requests_version = "Error %s" % e

    try:
        import conda_build
    except ImportError:
        conda_build_version = "not installed"
    except Exception as e:
        conda_build_version = "Error %s" % e
    else:
        conda_build_version = conda_build.__version__

    # this is a hack associated with channel weight until we get the package cache reworked
    #   in a future release
    # for now, just ordering the channels for display in a semi-plausible way
    d = defaultdict(list)
    any(d[v[1]].append(k) for k, v in iteritems(get_channel_urls()))
    channels = list(chain.from_iterable(d[q] for q in sorted(d, reverse=True)))

    info_dict = dict(
        platform=subdir,
        conda_version=conda.__version__,
        conda_build_version=conda_build_version,
        root_prefix=root_dir,
        root_writable=root_writable,
        pkgs_dirs=pkgs_dirs,
        envs_dirs=envs_dirs,
        default_prefix=default_prefix,
        channels=channels,
        rc_path=rc_path,
        user_rc_path=user_rc_path,
        sys_rc_path=sys_rc_path,
        is_foreign=bool(foreign),
        envs=[],
        python_version='.'.join(map(str, sys.version_info)),
        requests_version=requests_version,
    )

    if args.unsafe_channels:
        if not args.json:
            print("\n".join(info_dict["channels"]))
        else:
            print(json.dumps({"channels": info_dict["channels"]}))
        return 0
    else:
        info_dict['channels'] = [hide_binstar_tokens(c) for c in
                                 info_dict['channels']]
    if args.all or args.json:
        for option in options:
            setattr(args, option, True)

    if args.all or all(not getattr(args, opt) for opt in options):
        for key in 'pkgs_dirs', 'envs_dirs', 'channels':
            info_dict['_' + key] = ('\n' + 24 * ' ').join(info_dict[key])
        info_dict['_rtwro'] = ('writable' if info_dict['root_writable'] else
                               'read only')
        print("""\
Current conda install:

             platform : %(platform)s
        conda version : %(conda_version)s
  conda-build version : %(conda_build_version)s
       python version : %(python_version)s
     requests version : %(requests_version)s
     root environment : %(root_prefix)s  (%(_rtwro)s)
  default environment : %(default_prefix)s
     envs directories : %(_envs_dirs)s
        package cache : %(_pkgs_dirs)s
         channel URLs : %(_channels)s
          config file : %(rc_path)s
    is foreign system : %(is_foreign)s
""" % info_dict)
        if not is_initialized():
            print("""\
# NOTE:
#     root directory '%s' is uninitialized""" % root_dir)

    if args.envs:
        common.handle_envs_list(info_dict['envs'], not args.json)

    if args.system and not args.json:
        from conda.cli.find_commands import find_commands, find_executable

        print("sys.version: %s..." % (sys.version[:40]))
        print("sys.prefix: %s" % sys.prefix)
        print("sys.executable: %s" % sys.executable)
        print("conda location: %s" % dirname(conda.__file__))
        for cmd in sorted(set(find_commands() + ['build'])):
            print("conda-%s: %s" % (cmd, find_executable('conda-' + cmd)))
        print("user site dirs: ", end='')
        site_dirs = get_user_site()
        if site_dirs:
            print(site_dirs[0])
        else:
            print()
        for site_dir in site_dirs[1:]:
            print('                %s' % site_dir)
        print()

        evars = ['PATH', 'PYTHONPATH', 'PYTHONHOME', 'CONDA_DEFAULT_ENV',
                 'CIO_TEST', 'CONDA_ENVS_PATH']
        if platform == 'linux':
            evars.append('LD_LIBRARY_PATH')
        elif platform == 'osx':
            evars.append('DYLD_LIBRARY_PATH')
        for ev in sorted(evars):
            print("%s: %s" % (ev, os.getenv(ev, '<not set>')))
        print()

    if args.license and not args.json:
        try:
            from _license import show_info
            show_info()
        except ImportError:
            print("""\
WARNING: could not import _license.show_info
# try:
# $ conda install -n root _license""")

    if args.json:
        common.stdout_json(info_dict)