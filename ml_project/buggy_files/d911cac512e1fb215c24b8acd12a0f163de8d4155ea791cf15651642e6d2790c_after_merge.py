    def _init_lineparser(self):
        bookmarks_directory = os.path.join(standarddir.config(), 'bookmarks')
        os.makedirs(bookmarks_directory, exist_ok=True)

        bookmarks_subdir = os.path.join('bookmarks', 'urls')
        self._lineparser = lineparser.LineParser(
            standarddir.config(), bookmarks_subdir, parent=self)