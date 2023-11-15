def rasa_x(args: argparse.Namespace):
    from rasa.cli.utils import print_success, print_error, signal_handler
    from rasa.core.utils import AvailableEndpoints

    signal.signal(signal.SIGINT, signal_handler)

    _configure_logging(args)

    if args.production:
        print_success("Starting Rasa X in production mode... 🚀")

        args.endpoints = get_validated_path(
            args.endpoints, "endpoints", DEFAULT_ENDPOINTS_PATH, True
        )
        endpoints = AvailableEndpoints.read_endpoints(args.endpoints)
        _rasa_service(args, endpoints)
    else:
        if not is_rasa_x_installed():
            print_error(
                "Rasa X is not installed. The `rasa x` "
                "command requires an installation of Rasa X."
            )
            sys.exit(1)

        project_path = "."

        if not is_rasa_project_setup(project_path):
            print_error(
                "This directory is not a valid Rasa project. Use 'rasa init' "
                "to create a new Rasa project or switch to a valid Rasa project "
                "directory."
            )
            sys.exit(1)

        if args.data and not os.path.exists(args.data):
            print_warning(
                "The provided data path ('{}') does not exists. Rasa X will start "
                "without any training data.".format(args.data)
            )

        # noinspection PyUnresolvedReferences
        from rasax.community import local

        local.check_license_and_metrics(args)

        rasa_x_token = generate_rasa_x_token()
        process = start_rasa_for_local_rasa_x(args, rasa_x_token=rasa_x_token)
        try:
            local.main(args, project_path, args.data, token=rasa_x_token)
        finally:
            process.terminate()