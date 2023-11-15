    def get_shell(self):
        """
        Return shell which is currently bound to Help,
        or another running shell if it has been terminated
        """
        if (not hasattr(self.shell, 'get_doc') or
                (hasattr(self.shell, 'is_running') and
                 not self.shell.is_running())):
            self.shell = None
            if self.main.ipyconsole is not None:
                shell = self.main.ipyconsole.get_current_shellwidget()
                if shell is not None and shell.kernel_client is not None:
                    self.shell = shell
            if self.shell is None:
                self.shell = self.internal_shell
        return self.shell