    def set_new_values(self, oper_combo, adding_all, selected_values=None):
        # def remove_children():
        #     for child in box.children()[1:]:
        #         box.layout().removeWidget(child)
        #         child.setParent(None)

        def add_textual(contents):
            le = gui.lineEdit(box, self, None,
                              sizePolicy=QSizePolicy(QSizePolicy.Expanding,
                                                     QSizePolicy.Expanding))
            if contents:
                le.setText(contents)
            le.setAlignment(Qt.AlignRight)
            le.editingFinished.connect(self.conditions_changed)
            return le

        def add_numeric(contents):
            le = add_textual(contents)
            le.setValidator(OWSelectRows.QDoubleValidatorEmpty())
            return le

        def add_datetime(contents):
            le = add_textual(contents)
            le.setValidator(QRegExpValidator(QRegExp(TimeVariable.REGEX)))
            return le

        box = self.cond_list.cellWidget(oper_combo.row, 2)
        lc = ["", ""]
        oper = oper_combo.currentIndex()
        attr_name = oper_combo.attr_combo.currentText()
        if attr_name in self.AllTypes:
            vtype = self.AllTypes[attr_name]
            var = None
        else:
            var = self.data.domain[attr_name]
            vtype = vartype(var)
            if selected_values is not None:
                lc = list(selected_values) + ["", ""]
                lc = [str(x) for x in lc[:2]]
        if box and vtype == box.var_type:
            lc = self._get_lineedit_contents(box) + lc

        if oper_combo.currentText().endswith(" defined"):
            label = QLabel()
            label.var_type = vtype
            self.cond_list.setCellWidget(oper_combo.row, 2, label)
        elif var is not None and var.is_discrete:
            if oper_combo.currentText().endswith(" one of"):
                if selected_values:
                    lc = [x for x in list(selected_values)]
                button = DropDownToolButton(self, var, lc)
                button.var_type = vtype
                self.cond_list.setCellWidget(oper_combo.row, 2, button)
            else:
                combo = QComboBox()
                combo.addItems([""] + var.values)
                if lc[0]:
                    combo.setCurrentIndex(int(lc[0]))
                else:
                    combo.setCurrentIndex(0)
                combo.var_type = vartype(var)
                self.cond_list.setCellWidget(oper_combo.row, 2, combo)
                combo.currentIndexChanged.connect(self.conditions_changed)
        else:
            box = gui.hBox(self, addToLayout=False)
            box.var_type = vtype
            self.cond_list.setCellWidget(oper_combo.row, 2, box)
            if vtype in (2, 4):  # continuous, time:
                validator = add_datetime if isinstance(var, TimeVariable) else add_numeric
                box.controls = [validator(lc[0])]
                if oper > 5:
                    gui.widgetLabel(box, " and ")
                    box.controls.append(validator(lc[1]))
            elif vtype == 3:  # string:
                box.controls = [add_textual(lc[0])]
                if oper in [6, 7]:
                    gui.widgetLabel(box, " and ")
                    box.controls.append(add_textual(lc[1]))
            else:
                box.controls = []
        if not adding_all:
            self.conditions_changed()