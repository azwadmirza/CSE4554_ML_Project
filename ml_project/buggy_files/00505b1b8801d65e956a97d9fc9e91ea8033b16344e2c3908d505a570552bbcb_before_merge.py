    def get_doc(self, objtxt):
        """Get object documentation dictionary"""
        wait_loop = QEventLoop()
        self.sig_got_reply.connect(wait_loop.quit)
        self.silent_exec_method("get_ipython().kernel.get_doc('%s')" % objtxt)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_got_reply.disconnect(wait_loop.quit)
        wait_loop = None

        return self._kernel_reply