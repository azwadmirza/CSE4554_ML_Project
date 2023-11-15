    def set_cwd(self, dirname):
        """Set shell current working directory."""
        code = u"get_ipython().kernel.set_cwd(r'{}')".format(dirname)
        if self._reading:
            self.kernel_client.input(u'!' + code)
        else:
            self.silent_execute(code)