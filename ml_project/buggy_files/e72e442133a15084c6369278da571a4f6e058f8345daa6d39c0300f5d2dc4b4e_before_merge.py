    def toggle_hscrollbar(self, checked):
        """Toggle horizontal scrollbar"""
        self.parent_widget.sig_option_changed.emit('show_hscrollbar', checked)
        self.show_hscrollbar = checked
        self.header().setStretchLastSection(not checked)
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        if PYQT5:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            self.header().setResizeMode(QHeaderView.ResizeToContents)