    def get_source(self, objtxt):
        """Get object source"""
        if self._reading:
            return
        wait_loop = QEventLoop()
        self.sig_got_reply.connect(wait_loop.quit)
        self.silent_exec_method("get_ipython().kernel.get_source('%s')" % objtxt)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_got_reply.disconnect(wait_loop.quit)
        wait_loop = None

        return self._kernel_reply