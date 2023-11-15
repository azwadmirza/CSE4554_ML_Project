def execute(args, parser):
    prefix = context.prefix_w_legacy_search

    regex = args.regex
    if args.full_name:
        regex = r'^%s$' % regex

    if args.revisions:
        from conda.history import History

        h = History(prefix)
        if isfile(h.path):
            if not args.json:
                h.print_log()
            else:
                stdout_json(h.object_log())
        else:
            raise CondaFileNotFoundError(h.path, "No revision log found: %s\n" % h.path)
        return

    if args.explicit:
        print_explicit(prefix, args.md5)
        return

    if args.canonical:
        format = 'canonical'
    elif args.export:
        print_explicit(prefix, args.md5)
        return
    else:
        format = 'human'

    if args.json:
        format = 'canonical'

    exitcode = print_packages(prefix, regex, format, piplist=args.pip,
                              json=args.json,
                              show_channel_urls=args.show_channel_urls)
    return exitcode