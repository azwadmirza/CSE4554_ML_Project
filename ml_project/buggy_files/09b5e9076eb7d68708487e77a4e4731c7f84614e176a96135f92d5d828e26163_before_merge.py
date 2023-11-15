    def __str__(self):  # pragma: no cover
        return (
            "Secret Type: %s\n"
            "Location:    %s:%d\n"
            # "Hash:        %s\n"
        ) % (
            self.type,
            self.filename, self.lineno,
            # self.secret_hash
        )