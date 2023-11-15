    def install(self):
        """Initialize installation process and show install widget."""
        self.setup(integration=False, welcome=False, installation=True)
        self._installation_thread.cancelled = False
        self._installation_thread.install()