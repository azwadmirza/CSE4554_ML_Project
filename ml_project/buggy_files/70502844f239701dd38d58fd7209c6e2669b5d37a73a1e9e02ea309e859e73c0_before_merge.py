    def __init__(self, parent):
        QWidget.__init__(self, parent)

        vert_layout = QVBoxLayout()

        # Type frame
        type_layout = QHBoxLayout()
        type_label = QLabel(_("Import as"))
        type_layout.addWidget(type_label)

        self.array_btn = array_btn = QRadioButton(_("array"))
        array_btn.setEnabled(ndarray is not FakeObject)
        array_btn.setChecked(ndarray is not FakeObject)
        type_layout.addWidget(array_btn)

        list_btn = QRadioButton(_("list"))
        list_btn.setChecked(not array_btn.isChecked())
        type_layout.addWidget(list_btn)

        if pd:
            self.df_btn = df_btn = QRadioButton(_("DataFrame"))
            df_btn.setChecked(False)
            type_layout.addWidget(df_btn)

        h_spacer = QSpacerItem(40, 20,
                               QSizePolicy.Expanding, QSizePolicy.Minimum)
        type_layout.addItem(h_spacer)
        type_frame = QFrame()
        type_frame.setLayout(type_layout)

        self._table_view = PreviewTable(self)
        vert_layout.addWidget(type_frame)
        vert_layout.addWidget(self._table_view)
        self.setLayout(vert_layout)