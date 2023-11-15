    def set_recent_files(self, recent_files):
        """Set a list of files opened by the project."""
        processed_recent_files = []
        for recent_file in recent_files:
            if os.path.isfile(recent_file):
                try:
                    relative_recent_file = os.path.relpath(
                        recent_file, self.root_path)
                    processed_recent_files.append(relative_recent_file)
                except ValueError:
                    processed_recent_files.append(recent_file)
        files = list(OrderedDict.fromkeys(processed_recent_files))
        self.config.set('main', 'recent_files', files)