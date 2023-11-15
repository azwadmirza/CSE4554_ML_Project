    def set_new_operators(self, attr_combo, adding_all,
                          selected_index=None, selected_values=None):
        oper_combo = QComboBox()
        oper_combo.row = attr_combo.row
        oper_combo.attr_combo = attr_combo
        var = self.data.domain[attr_combo.currentText()]
        oper_combo.addItems(self.operator_names[type(var)])
        oper_combo.setCurrentIndex(selected_index or 0)
        self.cond_list.setCellWidget(oper_combo.row, 1, oper_combo)
        self.set_new_values(oper_combo, adding_all, selected_values)
        oper_combo.currentIndexChanged.connect(
            lambda _: self.set_new_values(oper_combo, False))