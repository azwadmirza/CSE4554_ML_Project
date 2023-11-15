    def add_row(self, attr=None, condition_type=None, condition_value=None):
        model = self.cond_list.model()
        row = model.rowCount()
        model.insertRow(row)

        attr_combo = gui.OrangeComboBox(
            minimumContentsLength=12,
            sizeAdjustPolicy=QComboBox.AdjustToMinimumContentsLengthWithIcon)
        attr_combo.row = row
        for var in self._visible_variables(self.data.domain):
            if isinstance(var, Variable):
                attr_combo.addItem(*gui.attributeItem(var))
            else:
                attr_combo.addItem(var)
        if isinstance(attr, str):
            attr_combo.setCurrentText(attr)
        else:
            attr_combo.setCurrentIndex(
                attr or
                len(self.AllTypes) - (attr_combo.count() == len(self.AllTypes)))
        self.cond_list.setCellWidget(row, 0, attr_combo)

        index = QPersistentModelIndex(model.index(row, 3))
        temp_button = QPushButton('×', self, flat=True,
                                  styleSheet='* {font-size: 16pt; color: silver}'
                                             '*:hover {color: black}')
        temp_button.clicked.connect(lambda: self.remove_one(index.row()))
        self.cond_list.setCellWidget(row, 3, temp_button)

        self.remove_all_button.setDisabled(False)
        self.set_new_operators(attr_combo, attr is not None,
                               condition_type, condition_value)
        attr_combo.currentIndexChanged.connect(
            lambda _: self.set_new_operators(attr_combo, False))

        self.cond_list.resizeRowToContents(row)