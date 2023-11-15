    def get_conf(self):
        '''
        Combine the CherryPy configuration with the rest_cherrypy config values
        pulled from the master config and return the CherryPy configuration
        '''
        conf = {
            'global': {
                'server.socket_host': self.apiopts.get('host', '0.0.0.0'),
                'server.socket_port': self.apiopts.get('port', 8000),
                'server.thread_pool': self.apiopts.get('thread_pool', 100),
                'server.socket_queue_size': self.apiopts.get('queue_size', 30),
                'max_request_body_size': self.apiopts.get(
                    'max_request_body_size', 1048576),
                'debug': self.apiopts.get('debug', False),
                'log.access_file': self.apiopts.get('log_access_file', ''),
                'log.error_file': self.apiopts.get('log_error_file', ''),
            },
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),

                'tools.trailing_slash.on': True,
                'tools.gzip.on': True,

                'tools.html_override.on': True,
                'tools.cors_tool.on': True,
            },
        }

        if salt.utils.version_cmp(cherrypy.__version__, '12.0.0') < 0:
            # CherryPy >= 12.0 no longer supports "timeout_monitor", only set
            # this config option when using an older version of CherryPy.
            # See Issue #44601 for more information.
            conf['global']['engine.timeout_monitor.on'] = self.apiopts.get(
                'expire_responses', True
            )

        if cpstats and self.apiopts.get('collect_stats', False):
            conf['/']['tools.cpstats.on'] = True

        if 'favicon' in self.apiopts:
            conf['/favicon.ico'] = {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': self.apiopts['favicon'],
            }

        if self.apiopts.get('debug', False) is False:
            conf['global']['environment'] = 'production'

        # Serve static media if the directory has been set in the configuration
        if 'static' in self.apiopts:
            conf[self.apiopts.get('static_path', '/static')] = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': self.apiopts['static'],
            }

        # Add to global config
        cherrypy.config.update(conf['global'])

        return conf