    def startServer(self):
        if gevent_present:
            web.app.logger.info('Starting Gevent server')
            # leave subprocess out to allow forking for fetchers and processors
            self.start_gevent()
        else:
            try:
                web.app.logger.info('Starting Tornado server')
                if web.ub.config.get_config_certfile() and web.ub.config.get_config_keyfile():
                    ssl={"certfile": web.ub.config.get_config_certfile(),
                         "keyfile": web.ub.config.get_config_keyfile()}
                else:
                    ssl=None
                # Max Buffersize set to 200MB
                http_server = HTTPServer(WSGIContainer(web.app),
                            max_buffer_size = 209700000,
                            ssl_options=ssl)
                http_server.listen(web.ub.config.config_port)
                self.wsgiserver=IOLoop.instance()
                self.wsgiserver.start()
                # wait for stop signal
                self.wsgiserver.close(True)
            except SocketError as e:
                web.app.logger.info("Error starting server: %s" % e.strerror)
                print("Error starting server: %s" % e.strerror)
                web.helper.global_WorkerThread.stop()
                sys.exit(1)

        if self.restart == True:
            web.app.logger.info("Performing restart of Calibre-Web")
            web.helper.global_WorkerThread.stop()
            if os.name == 'nt':
                arguments = ["\"" + sys.executable + "\""]
                for e in sys.argv:
                    arguments.append("\"" + e + "\"")
                os.execv(sys.executable, arguments)
            else:
                os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            web.app.logger.info("Performing shutdown of Calibre-Web")
            web.helper.global_WorkerThread.stop()
        sys.exit(0)