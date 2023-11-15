    def show_log(self):
        if self.output:
            output_dialog = TextEditor(self.output, title=_("Profiler output"),
                                       readonly=True, parent=self)
            output_dialog.resize(700, 500)
            output_dialog.exec_()