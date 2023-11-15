    def get_recent_files(self):
        """Return a list of files opened by the project."""
        try:
            recent_files = self.CONF[WORKSPACE].get('main', 'recent_files',
                                                    default=[])
        except EnvironmentError:
            return []

        for recent_file in recent_files[:]:
            if not os.path.isfile(recent_file):
                recent_files.remove(recent_file)
        return list(OrderedDict.fromkeys(recent_files))