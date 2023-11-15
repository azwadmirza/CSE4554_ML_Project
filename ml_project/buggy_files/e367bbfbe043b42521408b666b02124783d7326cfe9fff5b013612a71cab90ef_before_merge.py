    def start(self):
        """ Create the LaunchManyCore instance and start it"""

        # Create engine with network thread
        startup_deferred = self.lm.register(self, self.sesslock)

        if self.get_libtorrent():
            self.load_checkpoint()

        self.sessconfig.set_callback(self.lm.sessconfig_changed_callback)

        return startup_deferred