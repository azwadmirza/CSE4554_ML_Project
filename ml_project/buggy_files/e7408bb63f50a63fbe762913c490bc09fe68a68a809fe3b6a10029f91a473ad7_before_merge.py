    def _examine_output(self, source, state, b_chunk, sudoable):
        '''
        Takes a string, extracts complete lines from it, tests to see if they
        are a prompt, error message, etc., and sets appropriate flags in self.
        Prompt and success lines are removed.

        Returns the processed (i.e. possibly-edited) output and the unprocessed
        remainder (to be processed with the next chunk) as strings.
        '''

        output = []
        for b_line in b_chunk.splitlines(True):
            display_line = to_text(b_line).rstrip('\r\n')
            suppress_output = False

            # display.debug("Examining line (source=%s, state=%s): '%s'" % (source, state, display_line))
            if self.become.expect_prompt() and self.become.check_password_prompt(b_line):
                display.debug("become_prompt: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_prompt'] = True
                suppress_output = True
            elif self.become.success and self.become.check_success(b_line):
                display.debug("become_success: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_success'] = True
                suppress_output = True
            elif sudoable and self.become.check_incorrect_password(b_line):
                display.debug("become_error: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_error'] = True
            elif sudoable and self.become.check_missing_password(b_line):
                display.debug("become_nopasswd_error: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_nopasswd_error'] = True

            if not suppress_output:
                output.append(b_line)

        # The chunk we read was most likely a series of complete lines, but just
        # in case the last line was incomplete (and not a prompt, which we would
        # have removed from the output), we retain it to be processed with the
        # next chunk.

        remainder = b''
        if output and not output[-1].endswith(b'\n'):
            remainder = output[-1]
            output = output[:-1]

        return b''.join(output), remainder