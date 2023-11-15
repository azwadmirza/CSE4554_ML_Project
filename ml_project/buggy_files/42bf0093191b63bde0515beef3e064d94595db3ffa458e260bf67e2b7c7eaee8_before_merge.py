    def list_databases(self):
        """
        List the databases available from the WFAU archive.
        """
        self.databases = set(self.all_databases + self._get_databases())
        return self.databases