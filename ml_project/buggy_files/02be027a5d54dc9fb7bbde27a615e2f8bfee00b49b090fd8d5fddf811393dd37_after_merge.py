    def receive(self, command=None, prompts=None, answer=None, newline=True, prompt_retry_check=False):
        '''
        Handles receiving of output from command
        '''
        recv = BytesIO()
        handled = False

        self._matched_prompt = None
        self._matched_cmd_prompt = None
        matched_prompt_window = window_count = 0

        while True:
            data = self._ssh_shell.recv(256)

            # when a channel stream is closed, received data will be empty
            if not data:
                break

            recv.write(data)
            offset = recv.tell() - 256 if recv.tell() > 256 else 0
            recv.seek(offset)

            window = self._strip(recv.read())
            window_count += 1

            if prompts and not handled:
                handled = self._handle_prompt(window, prompts, answer, newline)
                matched_prompt_window = window_count
            elif prompts and handled and prompt_retry_check and matched_prompt_window + 1 == window_count:
                # check again even when handled, if same prompt repeats in next window
                # (like in the case of a wrong enable password, etc) indicates
                # value of answer is wrong, report this as error.
                if self._handle_prompt(window, prompts, answer, newline, prompt_retry_check):
                    raise AnsibleConnectionFailure("For matched prompt '%s', answer is not valid" % self._matched_cmd_prompt)

            if self._find_prompt(window):
                self._last_response = recv.getvalue()
                resp = self._strip(self._last_response)
                return self._sanitize(resp, command)