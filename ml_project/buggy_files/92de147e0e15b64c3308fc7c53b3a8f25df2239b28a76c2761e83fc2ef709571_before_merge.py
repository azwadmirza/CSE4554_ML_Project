    def start_gevent(self):
        try:
            ssl_args = dict()
            if web.ub.config.get_config_certfile() and web.ub.config.get_config_keyfile():
                ssl_args = {"certfile": web.ub.config.get_config_certfile(),
                            "keyfile": web.ub.config.get_config_keyfile()}
            if os.name == 'nt':
                self.wsgiserver= WSGIServer(('0.0.0.0', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
            else:
                self.wsgiserver = WSGIServer(('', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
            self.wsgiserver.serve_forever()
        except SocketError:
            try:
                web.app.logger.info('Unable to listen on \'\', trying on IPv4 only...')
                self.wsgiserver = WSGIServer(('0.0.0.0', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
                self.wsgiserver.serve_forever()
            except (OSError, SocketError) as e:
                web.app.logger.info("Error starting server: %s" % e.strerror)
                print("Error starting server: %s" % e.strerror)
                web.helper.global_WorkerThread.stop()
                sys.exit(1)
        except Exception:
            web.app.logger.info("Unknown error while starting gevent")