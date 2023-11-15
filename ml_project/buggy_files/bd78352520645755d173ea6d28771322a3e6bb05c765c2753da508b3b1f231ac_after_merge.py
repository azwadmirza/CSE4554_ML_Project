    def __init__(
            self, variable: Categorical,
            data: Union[np.ndarray, List, MArray],
            selected_attributes: List[str], dialog_settings: Dict[str, Any],
            parent: QWidget = None, flags: Qt.WindowFlags = Qt.Dialog, **kwargs
    ) -> None:
        super().__init__(parent, flags, **kwargs)
        self.variable = variable
        self.data = data
        self.selected_attributes = selected_attributes

        # grouping strategy
        self.selected_radio = radio1 = QRadioButton("Group selected values")
        self.frequent_abs_radio = radio2 = QRadioButton(
            "Group values with less than"
        )
        self.frequent_rel_radio = radio3 = QRadioButton(
            "Group values with less than"
        )
        self.n_values_radio = radio4 = QRadioButton(
            "Group all except"
        )

        # if selected attributes available check the first radio button,
        # otherwise disable it
        if selected_attributes:
            radio1.setChecked(True)
        else:
            radio1.setEnabled(False)
            # they are remembered by number since radio button instance is
            # new object for each dialog
            checked = dialog_settings.get("selected_radio", 0)
            [radio2, radio3, radio4][checked].setChecked(True)

        label2 = QLabel("occurrences")
        label3 = QLabel("occurrences")
        label4 = QLabel("most frequent values")

        self.frequent_abs_spin = spin2 = QSpinBox()
        max_val = len(data)
        spin2.setMinimum(1)
        spin2.setMaximum(max_val)
        spin2.setValue(dialog_settings.get("frequent_abs_spin", 10))
        spin2.setMinimumWidth(
            self.fontMetrics().width("X") * (len(str(max_val)) + 1) + 20
        )
        spin2.valueChanged.connect(self._frequent_abs_spin_changed)

        self.frequent_rel_spin = spin3 = QDoubleSpinBox()
        spin3.setMinimum(0)
        spin3.setDecimals(1)
        spin3.setSingleStep(0.1)
        spin3.setMaximum(100)
        spin3.setValue(dialog_settings.get("frequent_rel_spin", 10))
        spin3.setMinimumWidth(self.fontMetrics().width("X") * (2 + 1) + 20)
        spin3.setSuffix(" %")
        spin3.valueChanged.connect(self._frequent_rel_spin_changed)

        self.n_values_spin = spin4 = QSpinBox()
        spin4.setMinimum(0)
        spin4.setMaximum(len(variable.categories))
        spin4.setValue(
            dialog_settings.get(
                "n_values_spin", min(10, len(variable.categories))
            )
        )
        spin4.setMinimumWidth(
            self.fontMetrics().width("X") * (len(str(max_val)) + 1) + 20
        )
        spin4.valueChanged.connect(self._n_values_spin_spin_changed)

        grid_layout = QGridLayout()
        # first row
        grid_layout.addWidget(radio1, 0, 0, 1, 2)
        # second row
        grid_layout.addWidget(radio2, 1, 0, 1, 2)
        grid_layout.addWidget(spin2, 1, 2)
        grid_layout.addWidget(label2, 1, 3)
        # third row
        grid_layout.addWidget(radio3, 2, 0, 1, 2)
        grid_layout.addWidget(spin3, 2, 2)
        grid_layout.addWidget(label3, 2, 3)
        # fourth row
        grid_layout.addWidget(radio4, 3, 0)
        grid_layout.addWidget(spin4, 3, 1)
        grid_layout.addWidget(label4, 3, 2, 1, 2)

        group_box = QGroupBox()
        group_box.setLayout(grid_layout)

        # grouped variable name
        new_name_label = QLabel("New value name: ")
        self.new_name_line_edit = n_line_edit = QLineEdit(
            dialog_settings.get("name_line_edit", self.DEFAULT_LABEL)
        )
        # it is shown gray when user removes the text and let user know that
        # word others is default one
        n_line_edit.setPlaceholderText(self.DEFAULT_LABEL)
        name_hlayout = QHBoxLayout()
        name_hlayout.addWidget(new_name_label)
        name_hlayout.addWidget(n_line_edit)

        # confirm_button = QPushButton("Apply")
        # cancel_button = QPushButton("Cancel")
        buttons = QDialogButtonBox(
            orientation=Qt.Horizontal,
            standardButtons=(QDialogButtonBox.Ok | QDialogButtonBox.Cancel),
            objectName="dialog-button-box",
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # join components
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(group_box)
        self.layout().addLayout(name_hlayout)
        self.layout().addWidget(buttons)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)