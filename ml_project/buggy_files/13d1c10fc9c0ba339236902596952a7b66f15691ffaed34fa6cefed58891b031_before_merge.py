    def _handle_input_request(self, msg):
        """Save history and add a %plot magic."""
        if self._hidden:
            raise RuntimeError(
                'Request for raw input during hidden execution.')

        # Make sure that all output from the SUB channel has been processed
        # before entering readline mode.
        self.kernel_client.iopub_channel.flush()
        self._input_ready = True
        if not self.is_debugging():
            return super(DebuggingWidget, self)._handle_input_request(msg)

        # While the widget thinks only one input is going on,
        # other functions can be sending messages to the kernel.
        # This must be properly processed to avoid dropping messages.
        # If the kernel was not ready, the messages are queued.
        if len(self._input_queue) > 0:
            msg = self._input_queue[0]
            del self._input_queue[0]
            self.kernel_client.input(msg)
            return

        def callback(line):
            # Save history to browse it later
            if not (len(self._control.history) > 0
                    and self._control.history[-1] == line):
                # do not save pdb commands
                cmd = line.split(" ")[0]
                if cmd and "do_" + cmd not in dir(pdb.Pdb):
                    self._control.history.append(line)

            # must match ConsoleWidget.do_execute
            self._executing = True

            # This is the Spyder addition: add a %plot magic to display
            # plots while debugging
            if line.startswith('%plot '):
                line = line.split()[-1]
                code = "__spy_code__ = get_ipython().run_cell('%s')" % line
                self.kernel_client.input(code)
            else:
                self.kernel_client.input(line)
            self._highlighter.highlighting_on = False
        self._highlighter.highlighting_on = True

        prompt, password = msg['content']['prompt'], msg['content']['password']
        position = self._prompt_pos

        if (self._reading and
                (prompt, password, position) == self._previous_prompt):
            # This is a duplicate, don't reprint
            # This can happen when sending commands to pdb from the frontend.
            return

        self._previous_prompt = (prompt, password, position)
        # Reset reading in case it was interrupted
        self._reading = False
        self._readline(prompt=prompt, callback=callback,
                       password=password)