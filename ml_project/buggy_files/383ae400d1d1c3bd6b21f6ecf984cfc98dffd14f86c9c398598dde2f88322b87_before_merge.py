    def open_edit_backends(self, sender=None, backend_id=None):
        if not self.edit_backends_dialog:
            self.edit_backends_dialog = BackendsDialog(self.req)
            self.edit_backends_dialog.dialog.insert_action_group('app', self)

        self.edit_backends_dialog.activate()
        if backend_id is not None:
            self.edit_backends_dialog.show_config_for_backend(backend_id)