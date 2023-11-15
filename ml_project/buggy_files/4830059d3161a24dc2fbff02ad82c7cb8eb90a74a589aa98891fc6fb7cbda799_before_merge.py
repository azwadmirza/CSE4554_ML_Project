def _livereload(host, port, config, builder, site_dir):

    # We are importing here for anyone that has issues with livereload. Even if
    # this fails, the --no-livereload alternative should still work.
    from livereload import Server
    import livereload.handlers

    class LiveReloadServer(Server):

        def get_web_handlers(self, script):
            handlers = super(LiveReloadServer, self).get_web_handlers(script)
            # replace livereload handler
            return [(handlers[0][0], _get_handler(site_dir, livereload.handlers.StaticFileHandler), handlers[0][2],)]

    server = LiveReloadServer()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config_file_path'], builder)

    for d in config['theme'].dirs:
        server.watch(d, builder)

    # Run `serve` plugin events.
    server = config['plugins'].run_event('serve', server, config=config)

    server.serve(root=site_dir, host=host, port=port, restart_delay=0)