    def __del__(self):
        try:
            self.delete()
        except OSError:
            pass