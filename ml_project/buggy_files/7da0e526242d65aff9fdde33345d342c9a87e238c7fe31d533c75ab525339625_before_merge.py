    def show_log(self):
        if self.output:
            TextEditor(self.output, title=_("Profiler output"),
                       readonly=True, size=(700, 500), parent=self).exec_()