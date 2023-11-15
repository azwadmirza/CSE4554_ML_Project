    def reset_to_default(self):
        """Reset to default values of the shortcuts making a confirmation."""
        reset = QMessageBox.warning(self, _("Shortcuts reset"),
                                    _("Do you want to reset "
                                      "to default values?"),
                                    QMessageBox.Yes | QMessageBox.No)
        if reset == QMessageBox.No:
            return
        CONF.reset_shortcuts()
        self.main.apply_shortcuts()
        self.table.load_shortcuts()
        self.load_from_conf()
        self.set_modified(False)