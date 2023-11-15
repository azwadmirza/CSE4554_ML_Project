    def show_errorlog(self):
        if self.error_output:
            output_dialog = TextEditor(self.error_output,
                                       title=_("Profiler output"),
                                       readonly=True, parent=self)
            output_dialog.resize(700, 500)
            output_dialog.exec_()