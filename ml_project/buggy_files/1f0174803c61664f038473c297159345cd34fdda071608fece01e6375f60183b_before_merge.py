    def silent_exec_input(self, code):
        """Silently execute code through stdin"""
        self._hidden = True

        # Wait until the kernel returns an answer
        wait_loop = QEventLoop()
        self.sig_input_reply.connect(wait_loop.quit)
        self.kernel_client.iopub_channel.flush()
        self.kernel_client.input(code)
        wait_loop.exec_()

        # Remove loop connection and loop
        self.sig_input_reply.disconnect(wait_loop.quit)
        wait_loop = None

        # Restore hidden state
        self._hidden = False

        # Emit signal
        if 'pdb_step' in code and self._input_reply is not None:
            fname = self._input_reply['fname']
            lineno = self._input_reply['lineno']
            self.sig_pdb_step.emit(fname, lineno)
        elif 'get_namespace_view' in code:
            view = self._input_reply
            self.sig_namespace_view.emit(view)
        elif 'get_var_properties' in code:
            properties = self._input_reply
            self.sig_var_properties.emit(properties)