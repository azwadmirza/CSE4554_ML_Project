    def is_defined(self, objtxt, force_import=False):
        """Return True if object is defined"""
        if self._reading:
            return
        wait_loop = QEventLoop()
        self.sig_got_reply.connect(wait_loop.quit)
        self.silent_exec_method(
            "get_ipython().kernel.is_defined('%s', force_import=%s)"
            % (objtxt, force_import))
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_got_reply.disconnect(wait_loop.quit)
        wait_loop = None

        return self._kernel_reply