    def interaction(self, frame, traceback):
        """
        Called when a user interaction is required.

        If this is from sigint, break on the upper frame.
        If the frame is in spydercustomize.py, quit.
        Notifies spyder and print current code.

        """
        if self._pdb_breaking:
            self._pdb_breaking = False
            if frame and frame.f_back:
                return self.interaction(frame.f_back, traceback)
        if (frame is not None
                and "spydercustomize.py" in frame.f_code.co_filename
                and "exec_code" == frame.f_code.co_name):
            self.onecmd('exit')
        else:
            self.setup(frame, traceback)
            if self.send_initial_notification:
                self.notify_spyder(frame)
            if get_ipython().kernel._pdb_print_code:
                self.print_stack_entry(self.stack[self.curindex])
            self._cmdloop()
            self.forget()