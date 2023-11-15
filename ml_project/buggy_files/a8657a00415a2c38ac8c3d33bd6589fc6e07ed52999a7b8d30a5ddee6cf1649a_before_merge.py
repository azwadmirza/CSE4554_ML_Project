    def close(self, force=False):
        '''
        Close the communication with the terminal's child and terminate it.
        '''
        if not self.closed:
            os.close(self.child_fd)
            os.close(self.child_fde)
            time.sleep(0.1)
            if not self.terminate(force):
                raise TerminalException('Failed to terminate child process.')
            self.child_fd = self.child_fde = None
            self.closed = True