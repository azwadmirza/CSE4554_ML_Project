    def write(self, data):
        self._register_log_path()

        # write into file
        self.file.write(data)
        # force flush to make sure `fetch_log` can get stdout in time
        self.file.flush()
        # write into previous stdout
        self.raw_stdout.write(data)