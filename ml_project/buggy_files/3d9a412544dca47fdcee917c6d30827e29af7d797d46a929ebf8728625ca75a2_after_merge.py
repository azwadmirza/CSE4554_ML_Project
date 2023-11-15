    def register(self):
        """
        Register this resource for later retrieval via lookup(), possibly in a child process.
        """
        os.environ[self.resourceEnvNamePrefix + self.pathHash] = self.pickle()