    def hardlink(self, src, dest):
        self.execute(f"ln {src} {dest}")