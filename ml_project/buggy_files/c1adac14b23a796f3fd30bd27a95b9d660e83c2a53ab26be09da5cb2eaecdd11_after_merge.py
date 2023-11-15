    def write(self, b):
        """
        Custom write method that calls out to onionshare_write_func
        """
        if not self.onionshare_request.stop_q.empty():
            self.close()
            self.onionshare_request.close()
            return

        bytes_written = self.f.write(b)
        self.onionshare_write_func(self.onionshare_filename, bytes_written)