    def hardlink(self, src, dest):
        dest = shlex.quote(dest)
        src = shlex.quote(src)
        self.execute(f"ln {src} {dest}")