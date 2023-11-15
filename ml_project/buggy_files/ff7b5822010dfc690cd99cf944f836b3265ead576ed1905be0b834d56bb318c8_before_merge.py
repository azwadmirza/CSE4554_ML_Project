    def start(self, port, stay_open=False, public_mode=False, persistent_slug=None):
        """
        Start the flask web server.
        """
        self.common.log('Web', 'start', 'port={}, stay_open={}, public_mode={}, persistent_slug={}'.format(port, stay_open, public_mode, persistent_slug))
        if not public_mode:
            self.generate_slug(persistent_slug)

        self.stay_open = stay_open

        # In Whonix, listen on 0.0.0.0 instead of 127.0.0.1 (#220)
        if os.path.exists('/usr/share/anon-ws-base-files/workstation'):
            host = '0.0.0.0'
        else:
            host = '127.0.0.1'

        self.running = True
        self.app.run(host=host, port=port, threaded=True)