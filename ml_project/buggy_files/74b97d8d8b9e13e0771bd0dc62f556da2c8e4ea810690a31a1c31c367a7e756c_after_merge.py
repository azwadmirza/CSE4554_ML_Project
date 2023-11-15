    def load_data(self, filename, ext):
        """Load data from a file."""
        overwrite = False
        if self.namespacebrowser.editor.var_properties:
            message = _('Do you want to overwrite old '
                        'variables (if any) in the namespace '
                        'when loading the data?')
            buttons = QMessageBox.Yes | QMessageBox.No
            result = QMessageBox.question(
                self, _('Data loading'), message, buttons)
            overwrite = result == QMessageBox.Yes
        try:
            return self.call_kernel(
                interrupt=True,
                blocking=True,
                timeout=CALL_KERNEL_TIMEOUT).load_data(
                    filename, ext, overwrite=overwrite)
        except TimeoutError:
            msg = _("Data is too big to be loaded")
            return msg
        except (UnpicklingError, RuntimeError):
            return None