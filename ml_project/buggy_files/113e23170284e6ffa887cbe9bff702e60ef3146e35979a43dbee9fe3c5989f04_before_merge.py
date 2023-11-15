    def show_errorlog(self):
        if self.error_output:
            TextEditor(self.error_output, title=_("Profiler output"),
                       readonly=True, size=(700, 500), parent=self).exec_()