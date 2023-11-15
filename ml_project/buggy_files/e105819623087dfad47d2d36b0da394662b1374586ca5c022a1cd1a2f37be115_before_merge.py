def main():
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    mongo_url = os.environ.get('MONGO_URL', env.get_mongo_url())
    wait_for_mongo_db_server(mongo_url)
    assert_mongo_db_version(mongo_url)

    populate_exporter_list()
    app = init_app(mongo_url)

    crt_path = os.path.join(MONKEY_ISLAND_ABS_PATH, 'cc', 'server.crt')
    key_path = os.path.join(MONKEY_ISLAND_ABS_PATH, 'cc', 'server.key')

    if env.is_debug():
        app.run(host='0.0.0.0', debug=True, ssl_context=(crt_path, key_path))
    else:
        http_server = HTTPServer(WSGIContainer(app),
                                 ssl_options={'certfile': os.environ.get('SERVER_CRT', crt_path),
                                              'keyfile': os.environ.get('SERVER_KEY', key_path)})
        http_server.listen(env.get_island_port())
        log_init_info()
        IOLoop.instance().start()