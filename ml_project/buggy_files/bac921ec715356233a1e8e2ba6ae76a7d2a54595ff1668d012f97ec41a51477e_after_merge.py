    def __init__(self, *args, **kw):
        super(BugzillaService, self).__init__(*args, **kw)
        self.base_uri = self.config.get('base_uri')
        self.username = self.config.get('username')
        self.ignore_cc = self.config.get('ignore_cc', default=False,
                                                 to_type=lambda x: x == "True")
        self.query_url = self.config.get('query_url', default=None)
        self.include_needinfos = self.config.get(
            'include_needinfos', False, to_type=lambda x: x == "True")
        self.open_statuses = self.config.get('open_statuses', _open_statuses, to_type=aslist)
        log.debug(" filtering on statuses: %r", self.open_statuses)

        # So more modern bugzilla's require that we specify
        # query_format=advanced along with the xmlrpc request.
        # https://bugzilla.redhat.com/show_bug.cgi?id=825370
        # ...but older bugzilla's don't know anything about that argument.
        # Here we make it possible for the user to specify whether they want
        # to pass that argument or not.
        self.advanced = asbool(self.config.get('advanced', 'no'))

        url = 'https://%s/xmlrpc.cgi' % self.base_uri
        api_key = self.config.get('api_key', default=None)
        if api_key:
            try:
                self.bz = bugzilla.Bugzilla(url=url, api_key=api_key)
            except TypeError:
                raise Exception("Bugzilla API keys require python-bugzilla>=2.1.0")
        else:
            password = self.get_password('password', self.username)
            self.bz = bugzilla.Bugzilla(url=url)
            self.bz.login(self.username, password)