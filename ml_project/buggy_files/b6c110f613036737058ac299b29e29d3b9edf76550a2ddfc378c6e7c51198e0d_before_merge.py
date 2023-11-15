def process(args):
    """Process the input from the CLI

    :param args: The parsed arguments
    :type args: :class:`argparse.Namespace`
    :param parser: the parser instance
    :type parser: :class:`argparse.ArgumentParser`
    :return: result of the selected action
    :rtype: str
    """
    if args.which == "bump":
        maptable = {'major': 'bump_major',
                    'minor': 'bump_minor',
                    'patch': 'bump_patch',
                    'prerelease': 'bump_prerelease',
                    'build': 'bump_build',
                    }
        ver = parse_version_info(args.version)
        # get the respective method and call it
        func = getattr(ver, maptable[args.bump])
        return str(func())

    elif args.which == "compare":
        return str(compare(args.version1, args.version2))