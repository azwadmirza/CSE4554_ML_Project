    def read1(self, n=-1):
        try:
            chunk = self.leftover or next(self.iterator)
        except StopIteration:
            return b""

        # Return an arbitrary number or bytes
        if n <= 0:
            self.leftover = None
            return chunk

        output, self.leftover = chunk[:n], chunk[n:]
        return output