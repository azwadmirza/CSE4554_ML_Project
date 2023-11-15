def interaction(self, frame, traceback):
    self.setup(frame, traceback)
    if self.send_initial_notification:
        self.notify_spyder(frame)
    self.print_stack_entry(self.stack[self.curindex])
    self._cmdloop()
    self.forget()