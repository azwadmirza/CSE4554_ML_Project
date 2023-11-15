    def __str__(self):  # pragma: no cover
        return (
            "Secret Type: %s\n"
            "Location:    %s:%d\n"
        ) % (
            self.type,
            self.filename, self.lineno,
        )