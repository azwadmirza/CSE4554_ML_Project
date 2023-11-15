    def __str__(self):
        return ' :: '.join(
            part for part in
            (self.typ, self.description, self.detail, self.title)
            if part is not None)