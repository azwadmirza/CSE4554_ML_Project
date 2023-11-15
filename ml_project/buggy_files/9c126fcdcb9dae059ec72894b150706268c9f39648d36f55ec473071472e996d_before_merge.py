def run(args: argparse.Namespace):
    import rasa.run

    args.endpoints = get_validated_path(
        args.endpoints, "endpoints", DEFAULT_ENDPOINTS_PATH, True
    )
    args.credentials = get_validated_path(
        args.credentials, "credentials", DEFAULT_CREDENTIALS_PATH, True
    )

    if args.enable_api:
        args.model = _validate_model_path(args.model, "model", DEFAULT_MODELS_PATH)
        rasa.run(**vars(args))

    # if the API is not enable you cannot start without a model
    # make sure either a model server, a remote storage, or a local model is
    # configured

    from rasa.model import get_model
    from rasa.core.utils import AvailableEndpoints

    # start server if remote storage is configured
    if args.remote_storage is not None:
        rasa.run(**vars(args))

    # start server if model server is configured
    endpoints = AvailableEndpoints.read_endpoints(args.endpoints)
    model_server = endpoints.model if endpoints and endpoints.model else None
    if model_server is not None:
        rasa.run(**vars(args))

    # start server if local model found
    args.model = _validate_model_path(args.model, "model", DEFAULT_MODELS_PATH)
    local_model_set = True
    try:
        get_model(args.model)
    except ModelNotFound:
        local_model_set = False

    if local_model_set:
        rasa.run(**vars(args))

    print_error(
        "No model found. You have three options to provide a model:\n"
        "1. Configure a model server in the endpoint configuration and provide "
        "the configuration via '--endpoints'.\n"
        "2. Specify a remote storage via '--remote-storage' to load the model "
        "from.\n"
        "3. Train a model before running the server using `rasa train` and "
        "use '--model' to provide the model path.\n"
        "For more information check {}.".format(
            DOCS_BASE_URL + "/user-guide/running-the-server/"
        )
    )