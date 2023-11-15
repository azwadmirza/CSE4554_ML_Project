def execute(args, parser):
    from ..base.context import context

    if args.root:
        if context.json:
            stdout_json({'root_prefix': context.root_prefix})
        else:
            print(context.root_prefix)
        return

    if args.packages:
        print_package_info(args.packages)
        return

    if args.unsafe_channels:
        if not context.json:
            print("\n".join(context.channels))
        else:
            print(json.dumps({"channels": context.channels}))
        return 0

    options = 'envs', 'system', 'license'

    if args.all or context.json:
        for option in options:
            setattr(args, option, True)

    info_dict = get_info_dict(args.system)

    if (args.all or all(not getattr(args, opt) for opt in options)) and not context.json:
        print_main_info(info_dict)

    if args.envs:
        handle_envs_list(info_dict['envs'], not context.json)

    if args.system:
        if not context.json:
            from .find_commands import find_commands, find_executable
            print("sys.version: %s..." % (sys.version[:40]))
            print("sys.prefix: %s" % sys.prefix)
            print("sys.executable: %s" % sys.executable)
            print("conda location: %s" % info_dict['conda_location'])
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

            for name, value in sorted(iteritems(info_dict['env_vars'])):
                print("%s: %s" % (name, value))
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