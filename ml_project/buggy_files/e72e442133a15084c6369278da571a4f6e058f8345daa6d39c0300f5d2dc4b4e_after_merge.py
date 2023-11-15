    def toggle_hscrollbar(self, checked):
        """Toggle horizontal scrollbar"""
        self.parent_widget.sig_option_changed.emit('show_hscrollbar', checked)
        self.show_hscrollbar = checked
        self.header().setStretchLastSection(not checked)
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        try:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        except:  # support for qtpy<1.2.0
            self.header().setResizeMode(QHeaderView.ResizeToContents)