    def startServer(self):
        if gevent_present:
            web.app.logger.info('Starting Gevent server')
            # leave subprocess out to allow forking for fetchers and processors
            self.start_gevent()
        else:
            try:
                ssl = None
                web.app.logger.info('Starting Tornado server')
                certfile_path   = web.ub.config.get_config_certfile()
                keyfile_path    = web.ub.config.get_config_keyfile()
                if certfile_path and keyfile_path:
                    if os.path.isfile(certfile_path) and os.path.isfile(keyfile_path):
                        ssl = {"certfile": certfile_path,
                               "keyfile": keyfile_path}
                    else:
                        web.app.logger.info('The specified paths for the ssl certificate file and/or key file seem to be broken. Ignoring ssl. Cert path: %s | Key path: %s' % (certfile_path, keyfile_path))

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

        # ToDo: Somehow caused by circular import under python3 refactor
        if sys.version_info > (3, 0):
            self.restart = web.py3_restart_Typ
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