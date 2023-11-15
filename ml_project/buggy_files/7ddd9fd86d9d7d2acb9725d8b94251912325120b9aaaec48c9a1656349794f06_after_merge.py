    def __init__(self, parent, title, main_text, buttons, show_input=False, checkbox_text=None):
        DialogContainer.__init__(self, parent)

        uic.loadUi(get_ui_file_path('buttonsdialog.ui'), self.dialog_widget)

        self.dialog_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.dialog_widget.dialog_title_label.setText(title)

        self.dialog_widget.dialog_main_text_label.setText(main_text)
        self.dialog_widget.dialog_main_text_label.adjustSize()
        self.checkbox = self.dialog_widget.checkbox

        if not show_input:
            self.dialog_widget.dialog_input.setHidden(True)
        else:
            connect(self.dialog_widget.dialog_input.returnPressed, lambda: self.button_clicked.emit(0))

        if not checkbox_text:
            self.dialog_widget.checkbox.setHidden(True)
        else:
            self.dialog_widget.checkbox.setText(checkbox_text)

        hspacer_left = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dialog_widget.dialog_button_container.layout().addSpacerItem(hspacer_left)

        self.buttons = []
        for index in range(len(buttons)):
            self.create_button(index, *buttons[index])

        hspacer_right = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dialog_widget.dialog_button_container.layout().addSpacerItem(hspacer_right)
        if hasattr(self.window(), 'escape_pressed'):
            connect(self.window().escape_pressed, self.close_dialog)
        self.on_main_window_resize()