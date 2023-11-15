    def __repr__(self):
        def e(v):
            return v.decode("utf-8") if isinstance(v, bytes) else v

        cmd_repr = e(" ").join(pipes.quote(e(c)) for c in self.cmd)
        if self.env is not None:
            cmd_repr += e(" env of {!r}").format(self.env)
        return cmd_repr