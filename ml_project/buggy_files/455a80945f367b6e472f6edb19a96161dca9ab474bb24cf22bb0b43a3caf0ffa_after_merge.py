def serve(config, options=None):
    """
    Start the devserver, and rebuild the docs whenever any changes take effect.
    """
    # Create a temporary build directory, and set some options to serve it
    tempdir = tempfile.mkdtemp()
    options['site_dir'] = tempdir

    # Only use user-friendly URLs when running the live server
    options['use_directory_urls'] = True

    # Perform the initial build
    config = load_config(options=options)
    build(config, live_server=True)

    # Note: We pass any command-line options through so that we
    #       can re-apply them if the config file is reloaded.
    event_handler = BuildEventHandler(options)
    config_event_handler = ConfigEventHandler(options)

    # We could have used `Observer()`, which can be faster, but
    # `PollingObserver()` works more universally.
    observer = PollingObserver()
    observer.schedule(event_handler, config['docs_dir'], recursive=True)
    for theme_dir in config['theme_dir']:
        if not os.path.exists(theme_dir):
            continue
        observer.schedule(event_handler, theme_dir, recursive=True)
    observer.schedule(config_event_handler, '.')
    observer.start()

    class TCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    class DocsDirectoryHandler(FixedDirectoryHandler):
        base_dir = config['site_dir']

    host, port = config['dev_addr'].split(':', 1)
    server = TCPServer((host, int(port)), DocsDirectoryHandler)

    print('Running at: http://%s:%s/' % (host, port))
    print('Live reload enabled.')
    print('Hold ctrl+c to quit.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping server...')

    # Clean up
    observer.stop()
    observer.join()
    shutil.rmtree(tempdir)
    print('Quit complete')