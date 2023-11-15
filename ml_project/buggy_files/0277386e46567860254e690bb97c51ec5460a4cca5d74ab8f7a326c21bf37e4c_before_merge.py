    def remote_input_older_than_local(self):
        files = set()
        for f in self.remote_input:
            if (f.exists_remote and f.exists_local) and (f.mtime < f.mtime_local):
                files.add(f)
        return files