    def start(self):
        """
        Start a Tribler session by initializing the LaunchManyCore class.
        Returns a deferred that fires when the Tribler session is ready for use.
        """
        startup_deferred = self.lm.register(self, self.sesslock)

        def load_checkpoint(_):
            if self.get_libtorrent():
                self.load_checkpoint()

        self.sessconfig.set_callback(self.lm.sessconfig_changed_callback)

        return startup_deferred.addCallback(load_checkpoint)