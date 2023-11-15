    def set_cwd(self, dirname):
        """Set shell current working directory."""
        return self.silent_execute(
            u"get_ipython().kernel.set_cwd(r'{}')".format(dirname))