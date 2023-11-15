    def remote_output_older_than_local(self):
        files = set()
        for f in self.remote_output:
            if (f.exists_remote and f.exists_local) and (f.mtime < f.mtime_local):
                files.add(f)
        return files