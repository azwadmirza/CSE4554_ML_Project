    def run(self):
        '''
        Run the api
        '''
        import salt.client.netapi
        self.parse_args()
        self.setup_logfile_logger()
        verify_log(self.config)
        self.daemonize_if_required()
        client = salt.client.netapi.NetapiClient(self.config)
        self.set_pidfile()
        client.run()