    def __init__(self, parent, model, header, hscroll, vscroll):
        """Constructor."""
        QTableView.__init__(self, parent)
        self.setModel(model)
        self.setHorizontalScrollBar(hscroll)
        self.setVerticalScrollBar(vscroll)
        self.setHorizontalScrollMode(1)
        self.setVerticalScrollMode(1)

        self.sort_old = [None]
        self.header_class = header
        self.header_class.sectionClicked.connect(self.sortByColumn)
        self.menu = self.setup_menu()
        CONF.config_shortcut(
            self.copy,
            context='variable_explorer',
            name='copy',
            parent=self)
        self.horizontalScrollBar().valueChanged.connect(
                        lambda val: self.load_more_data(val, columns=True))
        self.verticalScrollBar().valueChanged.connect(
                        lambda val: self.load_more_data(val, rows=True))