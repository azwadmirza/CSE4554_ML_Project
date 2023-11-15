    def __init__(self, parent, model, dtype, shape):
        QTableView.__init__(self, parent)

        self.setModel(model)
        self.setItemDelegate(ArrayDelegate(dtype, self))
        total_width = 0
        for k in range(shape[1]):
            total_width += self.columnWidth(k)
        self.viewport().resize(min(total_width, 1024), self.height())
        self.shape = shape
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