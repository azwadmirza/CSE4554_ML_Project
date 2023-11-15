    def __next__(self) -> bytes:
        return next(self.reader).encode("utf-8")