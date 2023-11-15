    def copy(self, src, dest):
        self.execute(f"cp {src} {dest}")