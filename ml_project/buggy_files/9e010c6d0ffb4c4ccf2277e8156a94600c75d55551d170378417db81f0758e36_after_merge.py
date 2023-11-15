    def _open_images(self):
        """Add image files from the menubar."""
        filenames, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select image(s)...',
            directory=self._last_visited_dir,  # home dir by default
        )
        if filenames is not None:
            self._add_files(filenames)