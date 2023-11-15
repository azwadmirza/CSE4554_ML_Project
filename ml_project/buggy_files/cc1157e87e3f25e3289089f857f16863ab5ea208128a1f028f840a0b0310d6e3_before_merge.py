    def load(self):
        """ Load user settings file from disk, merging with allowed settings in default settings file.
        Creates user settings if missing. """

        # Default and user settings objects
        default_settings, user_settings = {}, {}

        # try to load default settings, on failure will raise exception to caller
        default_settings = self.read_from_file(self.default_settings_filename)

        # Try to find user settings file
        file_path = os.path.join(info.USER_PATH, self.settings_filename)

        # Load user settings (if found)
        if os.path.exists(os.fsencode(file_path)):

            # Will raise exception to caller on failure to read
            try:
                user_settings = self.read_from_file(file_path)
            except Exception as ex:
                log.error("Error loading settings file: %s" % ex)

                _ = QCoreApplication.instance()._tr
                QMessageBox.warning(None, _("Settings Error"),
                                          _("Error loading settings file: %(file_path)s. Settings will be reset.") % { "file_path": file_path})
                user_settings = {}

        # Merge default and user settings, excluding settings not in default, Save settings
        self._data = self.merge_settings(default_settings, user_settings)

        # Return success of saving user settings file back after merge
        return self.write_to_file(file_path, self._data)