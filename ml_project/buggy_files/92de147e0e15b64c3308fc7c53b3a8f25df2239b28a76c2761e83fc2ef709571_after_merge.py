    def start_gevent(self):
        try:
            ssl_args = dict()
            certfile_path   = web.ub.config.get_config_certfile()
            keyfile_path    = web.ub.config.get_config_keyfile()
            if certfile_path and keyfile_path:
                if os.path.isfile(certfile_path) and os.path.isfile(keyfile_path):
                    ssl_args = {"certfile": certfile_path,
                                "keyfile": keyfile_path}
                else:
                    web.app.logger.info('The specified paths for the ssl certificate file and/or key file seem to be broken. Ignoring ssl. Cert path: %s | Key path: %s' % (certfile_path, keyfile_path))
            if os.name == 'nt':
                self.wsgiserver= WSGIServer(('0.0.0.0', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
            else:
                self.wsgiserver = WSGIServer(('', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
            web.py3_gevent_link = self.wsgiserver
            self.wsgiserver.serve_forever()

        except SocketError:
            try:
                web.app.logger.info('Unable to listen on \'\', trying on IPv4 only...')
                self.wsgiserver = WSGIServer(('0.0.0.0', web.ub.config.config_port), web.app, spawn=Pool(), **ssl_args)
                web.py3_gevent_link = self.wsgiserver
                self.wsgiserver.serve_forever()
            except (OSError, SocketError) as e:
                web.app.logger.info("Error starting server: %s" % e.strerror)
                print("Error starting server: %s" % e.strerror)
                web.helper.global_WorkerThread.stop()
                sys.exit(1)
        except Exception:
            web.app.logger.info("Unknown error while starting gevent")