    def restart(self):
        """
        Restart the console

        This is needed when we switch projects to update PYTHONPATH
        and the selected interpreter
        """
        self.master_clients = 0
        self.create_new_client_if_empty = False
        for i in range(len(self.clients)):
            client = self.clients[-1]
            try:
                client.shutdown()
            except Exception as e:
                QMessageBox.warning(self, _('Warning'),
                    _("It was not possible to restart the IPython console "
                      "when switching to this project. "
                      "The error was {0}").format(e), QMessageBox.Ok)
            self.close_client(client=client, force=True)
        self.create_new_client(give_focus=False)
        self.create_new_client_if_empty = True