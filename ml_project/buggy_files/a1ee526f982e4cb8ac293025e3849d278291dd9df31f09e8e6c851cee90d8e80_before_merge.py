def start_infra(asynchronous=False, apis=None):
    try:
        # load plugins
        load_plugins()

        event_publisher.fire_event(event_publisher.EVENT_START_INFRA,
            {'d': in_docker() and 1 or 0, 'c': in_ci() and 1 or 0})

        # set up logging
        setup_logging()

        # prepare APIs
        apis = canonicalize_api_names(apis)
        # set environment
        os.environ['AWS_REGION'] = config.DEFAULT_REGION
        os.environ['ENV'] = ENV_DEV
        # register signal handlers
        if not os.environ.get(ENV_INTERNAL_TEST_RUN):
            register_signal_handlers()
        # make sure AWS credentials are configured, otherwise boto3 bails on us
        check_aws_credentials()
        # install libs if not present
        install.install_components(apis)
        # Some services take a bit to come up
        sleep_time = 5
        # start services
        thread = None

        if 'elasticsearch' in apis or 'es' in apis:
            sleep_time = max(sleep_time, 10)

        # loop through plugins and start each service
        for name, plugin in SERVICE_PLUGINS.items():
            if name in apis:
                t1 = plugin.start(asynchronous=True)
                thread = thread or t1

        time.sleep(sleep_time)
        # ensure that all infra components are up and running
        check_infra(apis=apis)
        # restore persisted data
        restore_persisted_data(apis=apis)
        print('Ready.')
        sys.stdout.flush()
        if not asynchronous and thread:
            # this is a bit of an ugly hack, but we need to make sure that we
            # stay in the execution context of the main thread, otherwise our
            # signal handlers don't work
            while True:
                time.sleep(1)
        return thread
    except KeyboardInterrupt:
        print('Shutdown')
    except Exception as e:
        print('Error starting infrastructure: %s %s' % (e, traceback.format_exc()))
        sys.stdout.flush()
        raise e
    finally:
        if not asynchronous:
            stop_infra()