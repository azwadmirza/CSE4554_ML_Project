    def set_recent_files(self, recent_files):
        """Set a list of files opened by the project."""
        for recent_file in recent_files[:]:
            if not os.path.isfile(recent_file):
                recent_files.remove(recent_file)
        recent_files = [os.path.relpath(recent_file, self.root_path)
                        for recent_file in recent_files]
        files = list(OrderedDict.fromkeys(recent_files))
        self.config.set('main', 'recent_files', files)