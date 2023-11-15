    def get_value(self, name):
        """Ask kernel for a value"""
        code = u"get_ipython().kernel.get_value('%s')" % name
        if self._reading:
            method = self.kernel_client.input
            code = u'!' + code
        else:
            method = self.silent_execute

        # Wait until the kernel returns the value
        wait_loop = QEventLoop()
        self.sig_got_reply.connect(wait_loop.quit)
        method(code)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_got_reply.disconnect(wait_loop.quit)
        wait_loop = None

        # Handle exceptions
        if self._kernel_value is None:
            if self._kernel_reply:
                msg = self._kernel_reply[:]
                self._kernel_reply = None
                raise ValueError(msg)

        return self._kernel_value