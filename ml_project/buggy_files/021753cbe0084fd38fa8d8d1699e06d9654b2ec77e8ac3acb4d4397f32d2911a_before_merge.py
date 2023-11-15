def execute(args, parser):
    from ..base.context import context
    from .common import stdout_json
    prefix = context.prefix_w_legacy_search
    regex = args.regex
    if args.full_name:
        regex = r'^%s$' % regex

    if args.revisions:
        from ..history import History
        h = History(prefix)
        if isfile(h.path):
            if not context.json:
                h.print_log()
            else:
                stdout_json(h.object_log())
        else:
            from ..exceptions import CondaFileNotFoundError
            raise CondaFileNotFoundError(h.path)
        return

    if args.explicit:
        print_explicit(prefix, args.md5)
        return

    if args.canonical:
        format = 'canonical'
    elif args.export:
        format = 'export'
    else:
        format = 'human'
    if context.json:
        format = 'canonical'

    exitcode = print_packages(prefix, regex, format, piplist=args.pip,
                              json=context.json,
                              show_channel_urls=context.show_channel_urls)
    return exitcode