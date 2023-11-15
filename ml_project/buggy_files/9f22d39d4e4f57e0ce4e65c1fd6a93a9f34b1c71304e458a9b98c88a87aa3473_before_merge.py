    def remove_autosave_file(self, filename):
        """
        Remove autosave file for specified file.

        This function also updates `self.name_mapping` and `self.file_hashes`.
        """
        if filename not in self.name_mapping:
            return
        autosave_filename = self.name_mapping[filename]
        try:
            os.remove(autosave_filename)
        except EnvironmentError as error:
            action = (_('Error while removing autosave file {}')
                      .format(autosave_filename))
            msgbox = AutosaveErrorDialog(action, error)
            msgbox.exec_if_enabled()
        del self.name_mapping[filename]
        del self.file_hashes[autosave_filename]
        self.save_autosave_mapping()
        logger.debug('Removing autosave file %s', autosave_filename)