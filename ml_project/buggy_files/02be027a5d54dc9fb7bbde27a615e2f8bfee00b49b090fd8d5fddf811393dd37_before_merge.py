    def receive(self, command=None, prompts=None, answer=None, newline=True):
        '''
        Handles receiving of output from command
        '''
        recv = BytesIO()
        handled = False

        self._matched_prompt = None

        while True:
            data = self._ssh_shell.recv(256)

            # when a channel stream is closed, received data will be empty
            if not data:
                break

            recv.write(data)
            offset = recv.tell() - 256 if recv.tell() > 256 else 0
            recv.seek(offset)

            window = self._strip(recv.read())
            if prompts and not handled:
                handled = self._handle_prompt(window, prompts, answer, newline)
            elif prompts and handled:
                # check again even when handled, a sub-prompt could be
                # repeating (like in the case of a wrong enable password, etc)
                self._handle_prompt(window, prompts, answer, newline)

            if self._find_prompt(window):
                self._last_response = recv.getvalue()
                resp = self._strip(self._last_response)
                return self._sanitize(resp, command)