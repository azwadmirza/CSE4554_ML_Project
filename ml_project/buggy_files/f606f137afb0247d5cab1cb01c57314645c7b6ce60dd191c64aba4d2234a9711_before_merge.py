    def set_filename(self, filename):
        """Set filename without performing code analysis."""
        filename = str(filename)  # filename is a QString instance
        self.kill_if_running()
        index, _data = self.get_data(filename)
        is_parent = self.parent is not None

        if filename not in self.curr_filenames:
            self.filecombo.insertItem(0, filename)
            self.curr_filenames.insert(0, filename)
            self.filecombo.setCurrentIndex(0)
        else:
            index = self.filecombo.findText(filename)
            self.filecombo.removeItem(index)
            self.curr_filenames.pop(index)
            self.filecombo.insertItem(0, filename)
            self.curr_filenames.insert(0, filename)
            self.filecombo.setCurrentIndex(0)

        num_elements = self.filecombo.count()
        if is_parent:
            if num_elements > self.parent.get_option('max_entries'):
                self.filecombo.removeItem(num_elements - 1)
        self.filecombo.selected()