    def _after_create_parent_question(self,
                                      force_overwrite, remember_directory):
        """After asking about parent directory.

        Args:
            force_overwrite: Force overwriting existing files.
            remember_directory: If True, remember the directory for future
                                downloads.
        """
        global last_used_directory

        try:
            os.makedirs(os.path.dirname(self._filename))
        except FileExistsError:
            pass
        except OSError as e:
            self._die(e.strerror)

        self.basename = os.path.basename(self._filename)
        if remember_directory:
            last_used_directory = os.path.dirname(self._filename)

        log.downloads.debug("Setting filename to {}".format(self._filename))
        if force_overwrite:
            self._after_set_filename()
        elif os.path.isfile(self._filename):
            # The file already exists, so ask the user if it should be
            # overwritten.
            txt = "<b>{}</b> already exists. Overwrite?".format(
                html.escape(self._filename))
            self._ask_confirm_question("Overwrite existing file?", txt)
        # FIFO, device node, etc. Make sure we want to do this
        elif (os.path.exists(self._filename) and
              not os.path.isdir(self._filename)):
            txt = ("<b>{}</b> already exists and is a special file. Write to "
                   "it anyways?".format(html.escape(self._filename)))
            self._ask_confirm_question("Overwrite special file?", txt)
        else:
            self._after_set_filename()