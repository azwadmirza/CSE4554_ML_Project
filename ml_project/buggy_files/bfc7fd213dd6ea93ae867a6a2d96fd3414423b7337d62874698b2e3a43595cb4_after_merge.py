    def get_dialog_directory(self, default=None):
        """
        Return the directory folder which a load/save dialog box should
        open into. In order of precedence this function will return:

        0) If not None, the value of default.
        1) The last location used by a load/save dialog.
        2) The directory containing the current file.
        3) The mode's reported workspace directory.
        """
        if default is not None:
            folder = default
        elif self.current_path and os.path.isdir(self.current_path):
            folder = self.current_path
        else:
            current_file_path = ""
            try:
                workspace_path = self.modes[self.mode].workspace_dir()
            except Exception as e:
                # Avoid crashing if workspace_dir raises, use default path
                # instead
                workspace_path = self.modes["python"].workspace_dir()
                logger.error(
                    (
                        "Could not open {} mode workspace directory"
                        'due to exception "{}". Using:'
                        "\n\n{}\n\n...to store your code instead"
                    ).format(self.mode, e, workspace_path)
                )
            tab = self._view.current_tab
            if tab and tab.path:
                current_file_path = os.path.dirname(os.path.abspath(tab.path))
            folder = current_file_path if current_file_path else workspace_path
        logger.info("Using path for file dialog: {}".format(folder))
        return folder