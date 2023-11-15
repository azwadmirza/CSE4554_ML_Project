def process(args):
    """Process the input from the CLI

    :param args: The parsed arguments
    :type args: :class:`argparse.Namespace`
    :param parser: the parser instance
    :type parser: :class:`argparse.ArgumentParser`
    :return: result of the selected action
    :rtype: str
    """
    if not hasattr(args, "which"):
        args.parser.print_help()
        raise SystemExit()
    elif args.which == "bump":
        maptable = {'major': 'bump_major',
                    'minor': 'bump_minor',
                    'patch': 'bump_patch',
                    'prerelease': 'bump_prerelease',
                    'build': 'bump_build',
                    }
        if args.bump is None:
            # When bump is called without arguments,
            # print the help and exit
            args.parser.parse_args([args.which, "-h"])

        ver = parse_version_info(args.version)
        # get the respective method and call it
        func = getattr(ver, maptable[args.bump])
        return str(func())

    elif args.which == "compare":
        return str(compare(args.version1, args.version2))