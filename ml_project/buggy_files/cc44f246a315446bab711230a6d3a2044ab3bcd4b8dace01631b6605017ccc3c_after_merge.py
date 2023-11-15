    def _insert_path(self, index, *, clicked=True):
        """Handle an element selection.

        Args:
            index: The QModelIndex of the selected element.
            clicked: Whether the element was clicked.
        """
        if index == QModelIndex():
            path = os.path.join(self._file_model.rootPath(), self._to_complete)
        else:
            path = os.path.normpath(self._file_model.filePath(index))

        if clicked:
            path += os.sep
        else:
            # On Windows, when we have C:\foo and tab over .., we get C:\
            path = path.rstrip(os.sep)

        log.prompt.debug('Inserting path {}'.format(path))
        self._lineedit.setText(path)
        self._lineedit.setFocus()
        self._set_fileview_root(path, tabbed=True)
        if clicked:
            # Avoid having a ..-subtree highlighted
            self._file_view.setCurrentIndex(QModelIndex())