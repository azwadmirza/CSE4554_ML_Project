    def _get_rel_path(self):
        """Return the relative path to the file if possible, else the parent dir.

        :return: relative path to file or parent dir to file
        :rtype: text_type
        """
        if app.TV_DOWNLOAD_DIR:
            try:
                rel_path = os.path.relpath(self.file_path, app.TV_DOWNLOAD_DIR)
                # check if we really found the relative path
                if not rel_path.startswith('..'):
                    return rel_path
            except ValueError:
                pass

        self._log(u"Couldn't get the relative path, using the parent folder instead", logger.DEBUG)
        parent_name = os.path.basename(os.path.dirname(self.file_path))
        # return self.file_path once this bug is fixed: goo.gl/U4XNoP
        return os.path.join(parent_name, self.file_name)