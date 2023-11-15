    def __exit__(self, exc_type, exc_value, traceback):
        try:
            os.rmdir(self.lock_path)
            os.rmdir(self.path)
        except OSError:
            pass