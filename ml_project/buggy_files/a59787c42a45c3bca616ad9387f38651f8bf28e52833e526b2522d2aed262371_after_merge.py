    def show_log(self):
        if self.output:
            output_dialog = TextEditor(
                self.output,
                title=_("Pylint output"),
                parent=self,
                readonly=True
            )
            output_dialog.resize(700, 500)
            output_dialog.exec_()