    def reset_namespace(self, force=False):
        """Reset the namespace by removing all names defined by the user."""
        reset_str = _("Reset IPython namespace")
        warn_str = _("All user-defined variables will be removed."
                     "<br>Are you sure you want to reset the namespace?")
        if not force:
            reply = QMessageBox.question(self, reset_str,
                                         warn_str,
                                         QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self._reading:
                    self.dbg_exec_magic('reset', '-f')
                else:
                    self.execute("%reset -f")
        else:
            if self._reading:
                self.dbg_exec_magic('reset', '-f')
            else:
                self.silent_execute("%reset -f")