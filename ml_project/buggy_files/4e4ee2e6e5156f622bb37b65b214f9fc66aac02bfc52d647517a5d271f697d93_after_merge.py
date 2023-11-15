    def path(self):
        if "raw_path" in self.scope:
            return self.scope["raw_path"].decode("latin-1")
        else:
            return self.scope["path"].decode("utf-8")