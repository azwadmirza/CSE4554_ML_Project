    def show_log(self):
        if self.output:
            TextEditor(self.output, title=_("Pylint output"), parent=self,
                       readonly=True, size=(700, 500)).exec_()