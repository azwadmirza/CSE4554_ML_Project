    def copy(self, src, dest):
        dest = shlex.quote(dest)
        src = shlex.quote(src)
        self.execute(f"cp {src} {dest}")