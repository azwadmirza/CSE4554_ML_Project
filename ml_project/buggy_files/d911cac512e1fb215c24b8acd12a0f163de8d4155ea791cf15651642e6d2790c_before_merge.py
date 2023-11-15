    def _init_lineparser(self):
        bookmarks_directory = os.path.join(standarddir.config(), 'bookmarks')
        if not os.path.isdir(bookmarks_directory):
            os.makedirs(bookmarks_directory)

        bookmarks_subdir = os.path.join('bookmarks', 'urls')
        self._lineparser = lineparser.LineParser(
            standarddir.config(), bookmarks_subdir, parent=self)