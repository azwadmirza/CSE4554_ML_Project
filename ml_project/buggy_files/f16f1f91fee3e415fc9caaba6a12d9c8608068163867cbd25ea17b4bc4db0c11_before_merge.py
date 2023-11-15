    def read(self, n=-1):
        chunk = self.reader(n)
        if self.is_text_file is None:
            self.is_text_file = istextblock(chunk)

        if self.is_text_file:
            data = dos2unix(chunk)
        else:
            data = chunk
        self.md5.update(data)

        return chunk