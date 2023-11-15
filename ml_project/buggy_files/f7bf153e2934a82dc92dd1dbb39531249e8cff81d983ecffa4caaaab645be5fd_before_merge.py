def main():
    parser = setup_parser()
    argcomplete.autocomplete(parser)
    options = parser.parse_args()

    _setup_logger(options)

    # Support the deprecated -c option
    if getattr(options, 'config', None) is not None:
        options.configs.append(options.config)

    config = Config.empty(**vars(options))

    try:
        command = options.command
        if not callable(command):
            command = getattr(
                importlib.import_module(command.rsplit('.', 1)[0]),
                command.rsplit('.', 1)[-1])

        # Set the process name to something cleaner
        process_name = [os.path.basename(sys.argv[0])]
        process_name.extend(sys.argv[1:])
        setproctitle(' '.join(process_name))
        command(config)
    except Exception:
        if not options.debug:
            raise
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])