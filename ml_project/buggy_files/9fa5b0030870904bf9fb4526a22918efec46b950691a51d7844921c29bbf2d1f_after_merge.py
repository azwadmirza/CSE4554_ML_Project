    def on_new_version_available(self, version):
        if version == str(self.gui_settings.value('last_reported_version')):
            return

        self.new_version_dialog = ConfirmationDialog(self, "New version available",
                                                     "Version %s of Tribler is available.Do you want to visit the "
                                                     "website to download the newest version?" % version,
                                                     [('IGNORE', BUTTON_TYPE_NORMAL), ('LATER', BUTTON_TYPE_NORMAL),
                                                      ('OK', BUTTON_TYPE_NORMAL)])
        self.new_version_dialog.button_clicked.connect(lambda action: self.on_new_version_dialog_done(version, action))
        self.new_version_dialog.show()