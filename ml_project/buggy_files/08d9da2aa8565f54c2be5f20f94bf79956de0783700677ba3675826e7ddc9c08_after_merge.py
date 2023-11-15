    def set_recent_files(self, recent_files):
        """Set a list of files opened by the project."""
        for recent_file in recent_files[:]:
            if not os.path.isfile(recent_file):
                recent_files.remove(recent_file)
        try:
            self.CONF[WORKSPACE].set('main', 'recent_files',
                                     list(OrderedDict.fromkeys(recent_files)))
        except EnvironmentError:
            pass