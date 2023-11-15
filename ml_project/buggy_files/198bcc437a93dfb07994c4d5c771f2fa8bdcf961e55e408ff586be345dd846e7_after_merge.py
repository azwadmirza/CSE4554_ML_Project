    def __init__(self, parent):
        """Constructor."""
        QTableView.__init__(self, parent)
        self.parent = parent
        self.setModel(parent.model())
        self.setFocusPolicy(Qt.NoFocus)
        self.verticalHeader().hide()
        try:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        except:  # support for qtpy<1.2.0
            self.horizontalHeader().setResizeMode(QHeaderView.Fixed)

        parent.viewport().stackUnder(self)

        self.setSelectionModel(parent.selectionModel())
        for col in range(1, parent.model().columnCount()):
            self.setColumnHidden(col, True)

        self.setColumnWidth(0, parent.columnWidth(0))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.show()

        self.setVerticalScrollMode(1)