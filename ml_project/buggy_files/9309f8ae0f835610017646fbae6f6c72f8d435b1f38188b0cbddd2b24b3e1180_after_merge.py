    def load_end(self):
        "internal: finished reading image data"
        while True:
            self.fp.read(4)  # CRC

            try:
                cid, pos, length = self.png.read()
            except (struct.error, SyntaxError):
                break

            if cid == b"IEND":
                break

            try:
                self.png.call(cid, pos, length)
            except UnicodeDecodeError:
                break
            except EOFError:
                ImageFile._safe_read(self.fp, length)
        self._text = self.png.im_text
        self.png.close()
        self.png = None