    def path(self):
        return (
            self.scope.get("raw_path", self.scope["path"].encode("latin-1"))
        ).decode("latin-1")