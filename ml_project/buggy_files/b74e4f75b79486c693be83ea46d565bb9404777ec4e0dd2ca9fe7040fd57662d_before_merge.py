def get_journal_name(args, config):
    from . import install

    args.journal_name = install.DEFAULT_JOURNAL_KEY
    if args.text and args.text[0] in config["journals"]:
        args.journal_name = args.text[0]
        args.text = args.text[1:]
    elif install.DEFAULT_JOURNAL_KEY not in config["journals"]:
        print("No default journal configured.", file=sys.stderr)
        print(list_journals(config), file=sys.stderr)
        sys.exit(1)

    logging.debug("Using journal name: %s", args.journal_name)
    return args