    def __init__(self, opts, eauth=None, quiet=False, parser=None):
        self.opts = opts
        self.eauth = eauth if eauth else {}
        self.quiet = quiet
        self.local = salt.client.get_local_client(opts['conf_file'])
        self.minions, self.ping_gen = self.__gather_minions()
        self.options = parser