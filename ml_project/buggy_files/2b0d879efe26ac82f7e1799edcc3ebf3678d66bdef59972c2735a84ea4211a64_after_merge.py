def cli(manual_args=None):
    try:
        if manual_args is None:
            manual_args = sys.argv[1:]

        args = parse_args(manual_args)
        configure_logger(args.debug)
        logging.debug("Parsed args: %s", args)

        return run(args)

    except JrnlError as e:
        print(e.message, file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        return 1