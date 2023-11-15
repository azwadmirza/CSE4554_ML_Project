    def __repr__(self):
        cmd_repr = " ".join(pipes.quote(c) for c in self.cmd)
        if self.env is not None:
            cmd_repr += " env of {!r}".format(self.env)
        return cmd_repr