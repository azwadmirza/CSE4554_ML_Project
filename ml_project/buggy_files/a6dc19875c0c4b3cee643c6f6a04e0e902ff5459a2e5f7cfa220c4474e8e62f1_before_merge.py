    def get_value(self, name):
        """Ask kernel for a value"""
        # Don't ask for values while reading (ipdb) is active
        if self._reading:
            raise ValueError(_("Inspecting and setting values while debugging "
                               "in IPython consoles is not supported yet by "
                               "Spyder."))

        # Wait until the kernel returns the value
        wait_loop = QEventLoop()
        self.sig_get_value.connect(wait_loop.quit)
        self.silent_execute("get_ipython().kernel.get_value('%s')" % name)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_get_value.disconnect(wait_loop.quit)
        wait_loop = None

        # Handle exceptions
        if self._kernel_value is None:
            if self._kernel_reply:
                msg = self._kernel_reply[:]
                self._kernel_reply = None
                raise ValueError(msg)

        return self._kernel_value